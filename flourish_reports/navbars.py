from django.conf import settings

from edc_navbar import NavbarItem, site_navbars, Navbar

flourish_reports = Navbar(name='flourish_reports')
no_url_namespace = True if settings.APP_NAME == 'flourish_reports' else False

flourish_reports.append_item(
    NavbarItem(name='recruitment_reports',
               label='Recruitment reports',
               fa_icon='fa-cogs',
               url_name='flourish_reports:recruitment_report_url'))

flourish_reports.append_item(
    NavbarItem(name='enrolment_reports',
               label='Enrolment reports',
               fa_icon='fa-cogs',
               url_name='flourish_reports:enrolment_report_url'))

flourish_reports.append_item(
    NavbarItem(name='download_reports',
               label='Download reports',
               fa_icon='fa-cogs',
               url_name='flourish_reports:download_report_url'))

flourish_reports.append_item(
    NavbarItem(name='missing_crf_dashboard',
               label='Missing Reports Summary',
               fa_icon='fa-cogs',
               url_name='flourish_reports:missing_crf_dashboard_url'))


flourish_reports.append_item(
    NavbarItem(name='missing_crf_report',
               label='Missing Reports Listboard',
               fa_icon='fa-cogs',
               url_name='flourish_reports:missing_crf_report_url'))

site_navbars.register(flourish_reports)
