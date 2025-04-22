from django.urls import path
from edc_dashboard import UrlConfig
from .admin_site import flourish_reports_admin
from .views import (
    EnrolmentReportView, RecruitmentReportView, FollowupReportView,
    DownloadReportView, CaregiverMissingCrfListView, CaregiverMissingReqListView,
    ChildMissingCrfListView, ChildMissingReqListView, MissingCrfTemplateView)


app_name = 'flourish_reports'

urlpatterns = [
    path('admin/', flourish_reports_admin.urls),
    path('recruitment', RecruitmentReportView.as_view(), name='recruitment_report_url'),
    path('download', DownloadReportView.as_view(), name='download_report_url'),
    path('enrolment', EnrolmentReportView.as_view(), name='enrolment_report_url'),
    path('followup', FollowupReportView.as_view(), name='followup_report_url'),
    path('missing_crf_dashboard', MissingCrfTemplateView.as_view(), name='missing_crf_dashboard_url')

]


missing_crf_report_listboard_url_config = UrlConfig(
    url_name='missing_crf_report_url',
    view_class=CaregiverMissingCrfListView,
    label='missing_crf_report',
    identifier_label='missing_crf_report_url')

missing_req_report_listboard_url_config = UrlConfig(
    url_name='missing_req_report_url',
    view_class=CaregiverMissingReqListView,
    label='missing_req_report',
    identifier_label='missing_req_report_url')

child_missing_crf_report_url_config = UrlConfig(
    url_name='child_missing_crf_report_url',
    view_class=ChildMissingCrfListView,
    label='child_missing_crf_report',
    identifier_label='child_missing_crf_report_url')

child_missing_req_report_url_config = UrlConfig(
    url_name='child_missing_req_report_url',
    view_class=ChildMissingReqListView,
    label='child_missing_req_report',
    identifier_label='child_missing_req_report_url')


urlpatterns += missing_crf_report_listboard_url_config.listboard_urls
urlpatterns += missing_req_report_listboard_url_config.listboard_urls
urlpatterns += child_missing_req_report_url_config.listboard_urls
urlpatterns += child_missing_crf_report_url_config.listboard_urls
