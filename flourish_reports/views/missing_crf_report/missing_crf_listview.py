import csv
import pandas as pd
from datetime import date
from typing import Any

from django.db.models import Model, Q
from django.apps import apps as django_apps
from django.db.models import OuterRef, Subquery, Count
from django.http import HttpRequest, HttpResponse
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin
from ...model_wrappers import CaregiverAppointmentModelWrapper
from .filters import MissingListboardViewFilters
from flourish_child.models import Appointment as ChildAppointments
from edc_metadata.models import CrfMetadata
from edc_metadata.constants import REQUIRED
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

    @property
    def maternal_visit_cls(self):
        return django_apps.get_model(self.maternal_visit_model)

    def get(self, request, *args, **kwargs) -> HttpResponse:

        download_request = request.GET.get('download', None)

        if download_request:

            crf_metadata_list = []

            for appointment in self.get_queryset():

                try:

                    crf_metadata_obj = CrfMetadata.objects.filter(
                        entry_status=REQUIRED,
                        subject_identifier=appointment.subject_identifier,
                        visit_code=appointment.visit_code,
                        visit_code_sequence=appointment.visit_code_sequence
                    )
                except CrfMetadata.DoesNotExist:
                    pass
                else:

                    temp_list = list(crf_metadata_obj.values(
                        'subject_identifier',
                        'schedule_name',
                        'visit_code',
                        'visit_code_sequence',
                        'model',
                        'entry_status'))

                    temp_list.append({
                        'appointment_status': appointment.appt_status,
                        'appointment_date': appointment.appt_datetime.date().isoformat()
                    })

                    df = pd.DataFrame(temp_list)

                    crf_metadata_list.append(df)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="missing_crf_{date.today().isoformat()}.csv"'

            concatenated_df = pd.concat(crf_metadata_list, axis=0, ignore_index=True)
            concatenated_df.to_csv(path_or_buf=response, index=False)

            return response

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        maternal_visits = self.maternal_visit_cls.objects.all()
        appt_id = list()

        for appt in queryset.only('id', 'appt_datetime'):

            crf_metadata = CrfMetadata.objects.filter(
                Q(created__lte=appt.appt_datetime) | Q(modified__lte=appt.appt_datetime),
                subject_identifier=appt.subject_identifier,
                visit_code=appt.visit_code,
                visit_code_sequence=appt.visit_code_sequence,
                entry_status=REQUIRED)

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
