from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from .follow_up_visualizations import FollowUpVisualizations
from ..view_mixins import DownloadReportMixin


class FollowupReportView(FollowUpVisualizations, EdcBaseViewMixin,
                         DownloadReportMixin, NavbarViewMixin,
                         TemplateView, LoginRequiredMixin):

    template_name = 'flourish_reports/followup_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'followup_reports'

    def get_success_url(self):
        return reverse('flourish_reports:followup_report_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {'expected_fu_table': self.expected_fu_df.to_html(
                classes=['table', 'table-striped'],
                table_id='expected_fu_dt',
                border=0,
                index=False),
             'expected_fu_pie': self.expected_fu_pie,
             'expected_fu_counts': self.expected_fu_counts,
             'completed_fu_table': self.completed_fu_df.to_html(
                 classes=['table', 'table-striped'],
                 table_id='completed_fu_dt',
                 border=0,
                 index=False),
             'completed_fu_hist': self.completed_fu_hist,
             'incomplete_fu_table': self.incomplete_fu_df.to_html(
                 classes=['table', 'table-striped'],
                 table_id='incompleted_fu_dt',
                 border=0,
                 index=False),
             'incomplete_fu_bar': self.incomplete_fu_bar,
             'complete_incomplete_fu_table': self.complete_incomplete_fu_table,
             'sq_enrol_table': self.sq_enrolled_before_fu_df.to_html(
                 classes=['table', 'table-striped'],
                 table_id='sq_enrolled_fu_dt',
                 border=0,
                 index=False),
             'sq_enrol_before_fu_table': self.sq_enrol_before_fu_table,
             'scheduled_fu_table': self.upcoming_scheduled_df.to_html(
                classes=['table', 'table-striped'],
                 table_id='scheduled_fu_dt',
                 border=0,
                 index=False)
             })
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
