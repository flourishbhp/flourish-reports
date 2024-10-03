import threading
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from plotly.offline import plot

from .followup_report_mixin import FollowupReportMixin

color_palette = {'cohort_a': '#00cc96',
                 'cohort_b': '#636efa',
                 'cohort_c': '#ef553b', }


class FollowUpVisualizations(FollowupReportMixin):

    def __init__(self):
        records = self.run_queries()
        self.expected_fu_list = records.get('expected_fus', [])
        self.sq_enrolled_list = records.get('sq_enrolled_before_fu', [])
        self.scheduled_list = records.get('upcoming_scheduled', [])
        self.completed_list = records.get('completed_fus', [])
        self.sq_completed_list = records.get('sq_completed_fus', [])
        self.incomplete_list = records.get('incomplete_fus', [])
        self.due_list = records.get('due_fus', [])

    def run_queries(self):
        records = {}
        query_functions = [self.expected_fus, self.sq_enrolled_before_fu,
                           self.upcoming_scheduled, ]

        # Create threads for each query function
        threads = [threading.Thread(target=func, args=(records,)) for func in query_functions]

        # Start all threads
        self.start_threads(threads)

        # Wait for all threads to finish
        self.await_threads(threads)

        # Execute functions dependent on the results
        threads = [threading.Thread(target=func, args=(records,)) for func in [self.completed_fus,
                                                                               self.due_for_fus]]

        # Start all threads
        self.start_threads(threads)

        # Wait for all threads to finish
        self.await_threads(threads)

        self.incomplete_fus(records)

        return records

    def start_threads(self, threads):
        # Start the threads
        for thread in threads:
            thread.start()

    def await_threads(self, threads):
        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    @property
    def expected_fu_df(self):
        return pd.DataFrame(
            self.expected_fu_list, columns=['subject_identifier', 'name', 'exposure_status',
                                            'child_age', 'enrollment_date', 'cohort_assign_date'])

    @property
    def due_fu_df(self):
        return pd.DataFrame(
            self.due_list, columns=['subject_identifier', 'name', 'exposure_status', 'child_age',
                                    'enrollment_date'])

    @property
    def completed_fu_df(self):
        return pd.DataFrame(
            self.completed_list, columns=['subject_identifier', 'name', 'exposure_status', 'child_age',
                                          'enrollment_date', 'fu_visit_date', 'neuro_crfs_nd'])

    @property
    def sq_completed_fu_df(self):
        return pd.DataFrame(
            self.sq_completed_list, columns=['subject_identifier', 'name', 'exposure_status', 'child_age',
                                             'enrollment_date', 'fu_visit_date'])

    @property
    def incomplete_fu_df(self):
        return pd.DataFrame(
            self.incomplete_list, columns=['subject_identifier', 'name', 'exposure_status',
                                           'enrollment_date', 'enrol_type'])

    @property
    def upcoming_scheduled_df(self):
        return pd.DataFrame(
            self.scheduled_list, columns=['subject_identifier', 'name', 'exposure_status',
                                          'scheduled_date'])

    @property
    def sq_enrolled_before_fu_df(self):
        return pd.DataFrame(
            self.sq_enrolled_list, columns=['subject_identifier', 'enrol_cohort', 'current_cohort'])

    @property
    def expected_fu_counts(self):
        expected_fu_per_cohort = self.expected_fu_df.groupby(
            ['name', 'exposure_status']).size().reset_index(name='expected_fu_count')

        return expected_fu_per_cohort.to_html(classes=['table', 'table-striped'], index=False)

    @property
    def expected_fu_pie(self):
        fig = px.pie(
            self.expected_fu_df, names='name', color='name',
            color_discrete_map=color_palette,
            title='Expected FUs by Cohort')
        pie_div = plot(fig, output_type='div')
        return pie_div

    @property
    def completed_fu_hist(self):
        completed_fu_df = self.completed_fu_df.sort_values(by='name')
        fig = px.histogram(
            completed_fu_df, x='fu_visit_date', color='name',
            color_discrete_map=color_palette,
            title='Completed FUs over time by Cohort')
        hist_div = plot(fig, output_type='div')
        return hist_div

    @property
    def incomplete_fu_bar(self):
        incomplete_per_cohort = self.incomplete_fu_df.groupby(
            ['name', 'exposure_status']).size().reset_index(name='pending_fu_count')

        fig = px.bar(
            incomplete_per_cohort, x='name', y='pending_fu_count',
            color='exposure_status',
            color_discrete_map=color_palette,
            barmode='group', title='Pending FUs by Cohort')
        bar_div = plot(fig, output_type='div')
        return bar_div

    @property
    def complete_incomplete_fu_table(self):
        completed_fu_df = pd.DataFrame(
            self.completed_list,
            columns=['subject_identifier', 'name', 'exposure_status', 'enrol_type', ])
        sq_completed_fu_df = pd.DataFrame(
            self.sq_completed_list,
            columns=['subject_identifier', 'name', 'exposure_status', 'enrol_type', ])
        incomplete_per_cohort = self.incomplete_fu_df.groupby(
            ['name', 'exposure_status', 'enrol_type']).size().reset_index(name='pending_fu')

        complete_per_cohort = completed_fu_df.groupby(
            ['name', 'exposure_status', 'enrol_type']).size().reset_index(name='completed_fu')

        sq_complete_per_cohort = sq_completed_fu_df.groupby(
            ['name', 'exposure_status', 'enrol_type']).size().reset_index(name='sq_completed_fu')

        fu_table = pd.merge(
            incomplete_per_cohort, complete_per_cohort,
            on=['name', 'exposure_status', 'enrol_type'], how='outer')
        fu_table = pd.merge(fu_table, sq_complete_per_cohort,
                            on=['name', 'exposure_status', 'enrol_type'], how='outer')

        fu_table.fillna(0, inplace=True)
        fu_table['pending_fu'] = fu_table['pending_fu'].astype(int)
        fu_table['completed_fu'] = fu_table['completed_fu'].astype(int)
        fu_table['sq_completed_fu'] = fu_table['sq_completed_fu'].astype(int)

        # Order by `cohort_name`
        fu_table = fu_table.sort_values(by='name')
        return fu_table.to_html(classes=['table', 'table-striped'], index=False)

    @property
    def sq_enrol_before_fu_table(self):
        sq_df = self.sq_enrolled_before_fu_df.groupby(
            ['enrol_cohort', 'current_cohort']).size().reset_index(name='count')

        return sq_df.to_html(classes=['table', 'table-striped'], index=False)
