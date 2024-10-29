from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from .aging_out_mixin import AgingOutMixin
from ..view_mixins import DownloadReportMixin
from ...classes import RecruitmentReport, SummaryReport
from ...classes.recruitment_reports import PieTotals
from ...models import ExportFile
from ...models import PieTotalStats, RecruitmentStats, TotalRecruitmentStats


class RecruitmentReportView(EdcBaseViewMixin, DownloadReportMixin,
                            NavbarViewMixin, TemplateView, LoginRequiredMixin,
                            AgingOutMixin):
    template_name = 'flourish_reports/recruit/recruitment_reports.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'flourish_reports'

    @property
    def study_stats(self):
        return RecruitmentStats.objects.all()

    @property
    def total_recruitment(self):
        return TotalRecruitmentStats.objects.first()

    @property
    def pie(self):
        return PieTotalStats.objects.first()

    def get_success_url(self):
        return reverse('flourish_reports:recruitment_report_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reports = RecruitmentReport()

        # Download reports
        download = self.request.GET.get('download', None)
        if download == "locator":
            self.download_data(description="Locator Data",
                               report_type="Locator Data", df=reports.locator_df)
        elif download == "worklist_data":
            self.download_data(description="Worklist Study Data",
                               report_type="Worklist Study Data", df=reports.randomised_df)
        elif download == "call_attempts":
            self.download_data(description="Call Attempts Data",
                               report_type="Call Attempts Data", df=reports.attempts_df)
        elif download == "continued_contact":
            self.download_data(description="Continued Contact Data",
                               report_type="Continued Contact Data", df=reports.to_call_df)
        elif download == "not_reacheble":
            self.download_data(description="Not Reacheble  Data",
                               report_type="Not Reacheble  Data", df=reports.not_reacheble_df)
        elif download == "declined":
            self.download_data(description="Declined  Data",
                               report_type="Declined  Data", df=reports.declined_df)
        elif download == "consented":
            self.download_data(description="Consented  Data",
                               report_type="Consented  Data", df=reports.consented_df)
        elif download == "summary":
            self.download_data(description="Summary  Data",
                               report_type="Summary  Data", df=reports.identifiers_summary_df)

        prev_study_data = []
        previous_studies = []

        total_expected = ['Total Expected']
        total_missing = ['Total Existing']
        total_existing = ['Total Missing']

        declined_data = []
        consented_data = []
        offstudy_data = []
        participants_not_reachable = []
        participants_to_call_again = []
        attempts_data = []

        expected_worklist = ['Expected Worklist']
        existing_worklist = ['Existing Worklist']
        missing_worklist = ['Missing Worklist']
        randomised = ['Randomised Worklist']
        not_randomised = ['Not randomised & not attempted Worklist']
        summary_pie = None
        total_attempts = None
        not_attempted = None

        for stats in self.study_stats:
            prev_study_data.append([stats.study, stats.dataset_total])
            previous_studies.append(stats.study)
            total_expected.append(stats.expected_locator)
            total_missing.append(stats.missing_locator)
            total_existing.append(stats.existing_locator)
            declined_data.append([stats.study, stats.declined])
            consented_data.append([stats.study, stats.consented])
            offstudy_data.append([stats.study, stats.offstudy])

            participants_not_reachable.append(
                [stats.study, stats.not_reacheble])
            participants_to_call_again.append(
                [stats.study, stats.participants_to_call])

            attempts_data.append(
                [stats.study, stats.study_participants, stats.total_attempts,
                 stats.total_not_attempted])

            expected_worklist.append(stats.expected_worklist)
            existing_worklist.append(stats.existing_worklist)
            missing_worklist.append(stats.missing_worklist)
            randomised.append(stats.randomised)
            not_randomised.append(stats.not_randomised)

        locator_report = [total_expected, total_existing, total_missing]
        worklist_report = [expected_worklist, existing_worklist,
                           missing_worklist, randomised, not_randomised]
        if self.total_recruitment:
            total_participants_to_call_again = self.total_recruitment.total_participants_to_call_again
            total_consented = self.total_recruitment.total_consented
            total_decline = self.total_recruitment.total_decline
            total_participants_not_reachable = self.total_recruitment.total_participants_not_reachable
            total_attempts = self.total_recruitment.total_attempts
            not_attempted = self.total_recruitment.not_attempted

            summary_pie = PieTotals(
                total_continued_contact=total_participants_to_call_again,
                total_consented=total_consented,
                total_unable_to_reach=total_participants_not_reachable,
                total_decline_uninterested=total_decline)

        attempts_prev_studies = [
            'Previous Study',
            'Total Study Participants',
            'Total Attempts',
            'Total not attempted']

        # Downloaed files
        locator_data_downloads = ExportFile.objects.filter(
            description="Locator Data").order_by('uploaded_at')
        worklist_data_downloads = ExportFile.objects.filter(
            description="Worklist Study Data").order_by('uploaded_at')
        call_attempts_data_downloads = ExportFile.objects.filter(
            description="Call Attempts Data").order_by('uploaded_at')
        continued_contact_data_downloads = ExportFile.objects.filter(
            description="Continued Contact Data").order_by('uploaded_at')
        not_reacheble_data_downloads = ExportFile.objects.filter(
            description="Not Reacheble  Data").order_by('uploaded_at')
        declined_data_downloads = ExportFile.objects.filter(
            description="Declined  Data").order_by('uploaded_at')
        consented_data_downloads = ExportFile.objects.filter(
            description="Consented  Data").order_by('uploaded_at')
        summary_data_downloads = ExportFile.objects.filter(
            description="Summary  Data").order_by('uploaded_at')

        table_defination = '<table class="fixed table table-hover table-sm table-condensed ">'
        summary_report = SummaryReport(study_stats=self.study_stats).summary_report.to_html()
        summary_report = summary_report.replace("<thead>", table_defination)
        context.update(
            # Downloads
            locator_data_downloads=locator_data_downloads,
            worklist_data_downloads=worklist_data_downloads,
            call_attempts_data_downloads=call_attempts_data_downloads,
            not_reacheble_data_downloads=not_reacheble_data_downloads,
            declined_data_downloads=declined_data_downloads,
            consented_data_downloads=consented_data_downloads,
            continued_contact_data_downloads=continued_contact_data_downloads,

            # Reports
            previous_studies=previous_studies,
            prev_study_data=prev_study_data,
            locator_report=locator_report,
            pie_chart=self.pie,
            worklist_report=worklist_report,
            attempts_prev_studies=attempts_prev_studies,
            attempts_data=attempts_data,
            total_attempts=total_attempts,
            not_attempted=not_attempted,
            participants_to_call_again=participants_to_call_again,
            participants_not_reachable=participants_not_reachable,
            declined=declined_data,
            consented=consented_data,
            summary_data_downloads=summary_data_downloads,
            summary_pie=summary_pie,
            ageing_out_statistics=self.ageing_out_statistics,

            # Summary report
            summary_report=summary_report
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

# TODO test again
