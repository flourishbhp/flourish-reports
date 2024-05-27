from datetime import date

import pandas as pd
from django.apps import apps as django_apps
from django.db.models import Q
from django.http import HttpResponse
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin
from edc_dashboard.views import ListboardView
from edc_metadata.constants import REQUIRED
from edc_metadata.models import CrfMetadata
from edc_navbar import NavbarViewMixin

from .filters import MissingListboardViewFilters
from ...model_wrappers import CaregiverAppointmentModelWrapper
from ...util import MigrationHelper


class MissingCrfListView(EdcBaseViewMixin,
                         NavbarViewMixin,
                         ListboardFilterViewMixin,
                         ListboardView):
    listboard_template = 'missing_crf_listboard_template'
    listboard_url = 'missing_crf_report_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = "far fa-user-circle"

    model = 'edc_appointment.appointment'
    model_wrapper_cls = CaregiverAppointmentModelWrapper
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crf_report'

    maternal_visit_model = 'flourish_caregiver.maternalvisit'

    listboard_view_filters = MissingListboardViewFilters()

    ordering = 'appt_datetime'

    crf_metadata = None

    caregiver_off_study_model = 'flourish_prn.caregiveroffstudy'

    @property
    def caregiver_off_study_cls(self):
        return django_apps.get_model(self.caregiver_off_study_model)

    @property
    def maternal_visit_cls(self):
        return django_apps.get_model(self.maternal_visit_model)

    def get(self, request, *args, **kwargs) -> HttpResponse:

        download_request = request.GET.get('download', None)

        if download_request:

            crf_metadata_list = []

            for appointment in self.get_queryset():
                crf_metadata_objs = self.crf_metadata_filter(appointment)

                for crf_metadata_obj in crf_metadata_objs:

                    is_off_study = False

                    offstudy_exists = self.caregiver_off_study_cls.objects.filter(
                        subject_identifier=appointment.subject_identifier).exists()
                    
                    model_cls = django_apps.get_model(crf_metadata_obj.model)
                    
                    migration_helper = MigrationHelper(model_cls._meta.app_label)

                    date_created = migration_helper.get_date_created(crf_metadata_obj.model)

                    if offstudy_exists:
                        is_off_study = True

                    temp = dict(
                        subject_identifier=crf_metadata_obj.subject_identifier,
                        visit_code=appointment.visit_code,
                        visit_code_sequence=appointment.visit_code_sequence,
                        schedule_name=appointment.schedule_name,
                        appointment_date=appointment.appt_datetime.date().isoformat(),
                        date_created = date_created.isoformat(),
                        appointment_status=appointment.appt_status,
                        crf_name=django_apps.get_model(
                            crf_metadata_obj.model)._meta.verbose_name,
                        entry_status=crf_metadata_obj.entry_status,
                        is_off_study="Off Study" if is_off_study else "On Study",
                        visit_date=appointment.maternalvisit.report_datetime.date().isoformat()

                    )

                    crf_metadata_list.append(temp)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="missing_crf_{date.today().isoformat()}.csv"'
            df = pd.DataFrame(crf_metadata_list)
            df.to_csv(path_or_buf=response, index=False)

            return response

        return super().get(request, *args, **kwargs)

    def crf_metadata_filter(self, appt):
        return CrfMetadata.objects.filter(
            Q(created__lte=appt.appt_datetime) | Q(modified__lte=appt.appt_datetime),
            subject_identifier=appt.subject_identifier,
            visit_code=appt.visit_code,
            visit_code_sequence=appt.visit_code_sequence,
            entry_status=REQUIRED)

    def get_queryset(self):
        queryset = super().get_queryset()

        maternal_visits = self.maternal_visit_cls.objects.all()
        appt_id = list()

        for appt in queryset.only('id', 'appt_datetime'):

            crf_metadata = self.crf_metadata_filter(appt)

            for crf_metadata_obj in crf_metadata:

                model_cls = django_apps.get_model(crf_metadata_obj.model)

                migration_helper = MigrationHelper(model_cls._meta.app_label)

                date_created = migration_helper.get_date_created(crf_metadata.model)

                if date_created and date_created < crf_metadata_obj.created.date():
                    continue

                appt_id.append(appt.id)

        return queryset.filter(
            maternalvisit__in=maternal_visits).filter(
            id__in=appt_id, )
