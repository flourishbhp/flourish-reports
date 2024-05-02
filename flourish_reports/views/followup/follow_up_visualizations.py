import threading
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from plotly.offline import plot

from .followup_report_mixin import FollowupReportMixin


class FollowUpVisualizations(FollowupReportMixin):

    def __init__(self):
        records = self.run_queries()
        self.expected_fu_list = records.get('expected_fus', [])
        self.sq_enrolled_list = records.get('sq_enrolled_before_fu', [])
        self.scheduled_list = records.get('upcoming_scheduled', [])
        self.completed_list = records.get('completed_fus', [])
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
            self.expected_fu_list, columns=['subject_identifier', 'name', 'child_age', 'enrollment_date'])

    @property
    def due_fu_df(self):
        return pd.DataFrame(
            self.due_list, columns=['subject_identifier', 'name', 'child_age', 'enrollment_date'])

    @property
    def completed_fu_df(self):
        return pd.DataFrame(
            self.completed_list, columns=['subject_identifier', 'name', 'child_age', 'enrollment_date', 'fu_visit_date'])

    @property
    def incomplete_fu_df(self):
        return pd.DataFrame(
            self.incomplete_list, columns=['subject_identifier', 'name', 'enrollment_date'])

    @property
    def upcoming_scheduled_df(self):
        return pd.DataFrame(
            self.scheduled_list, columns=['subject_identifier', 'name', 'scheduled_date'])

    @property
    def sq_enrolled_before_fu_df(self):
        return pd.DataFrame(
            self.sq_enrolled_list, columns=['subject_identifier', 'enrol_cohort', 'current_cohort'])

    @property
    def expected_fu_bar(self):
        fig = px.bar(
            self.expected_fu_df, x='name', title='Expected FUs by Cohort')
        bar_div = plot(fig, output_type='div')
        return bar_div

    @property
    def expected_fu_counts(self):
        expected_fu_per_cohort = self.expected_fu_df.groupby('name')['subject_identifier'].count().reset_index()
        expected_fu_per_cohort.columns = ['name', 'expected_fu_count']
        return expected_fu_per_cohort.to_html(classes=['table', 'table-striped'], index=False)

    @property
    def expected_fu_pie(self):
        fig = px.pie(
            self.expected_fu_df, names='name', title='Expected FUs by Cohort')
        pie_div = plot(fig, output_type='div')
        return pie_div

    @property
    def completed_fu_hist(self):
        fig = px.histogram(
            self.completed_fu_df, x='fu_visit_date', color='name', title='Completed FUs over time by Cohort')
        hist_div = plot(fig, output_type='div')
        return hist_div

    @property
    def incomplete_fu_bar(self):
        incomplete_per_cohort = self.incomplete_fu_df.groupby('name')['subject_identifier'].count().reset_index()
        incomplete_per_cohort.columns = ['name', 'pending_fu_count']

        fig = px.bar(
            incomplete_per_cohort, x='name', y='pending_fu_count', title='Pending FUs by Cohort')
        bar_div = plot(fig, output_type='div')
        return bar_div

    @property
    def complete_incomplete_fu_table(self):
        incomplete_per_cohort = self.incomplete_fu_df.groupby('name')['subject_identifier'].count().reset_index()
        incomplete_per_cohort.columns = ['name', 'pending_fu_count']

        complete_per_cohort = self.completed_fu_df.groupby('name')['subject_identifier'].count().reset_index()
        complete_per_cohort.columns = ['name', 'completed_fu_count']

        fu_table = pd.merge(
            incomplete_per_cohort, complete_per_cohort, on='name', how='outer')

        fu_table = fu_table.fillna(0)
        return fu_table.to_html(classes=['table', 'table-striped'], index=False)

    @property
    def sq_enrol_before_fu_table(self):
        sq_df = self.sq_enrolled_before_fu_df.groupby(
            ['enrol_cohort', 'current_cohort']).size().reset_index(name='count')

        return sq_df.to_html(classes=['table', 'table-striped'], index=False)
