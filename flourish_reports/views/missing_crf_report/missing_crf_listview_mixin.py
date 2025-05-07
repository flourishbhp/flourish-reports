import pandas as pd

from datetime import date
from django.apps import apps as django_apps
from django.db.models import OuterRef, Count, Subquery, IntegerField, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse

from edc_metadata.constants import REQUIRED


class MissingCRFListViewMixin:

    crf_metadata_model = 'edc_metadata.crfmetadata'
    caregiver_off_study_model = 'flourish_prn.caregiveroffstudy'

    @property
    def crf_metadata_cls(self):
        return django_apps.get_model(self.crf_metadata_model)

    @property
    def caregiver_off_study_cls(self):
        return django_apps.get_model(self.caregiver_off_study_model)

    def get_queryset(self):
        queryset = super().get_queryset()
        missing_crfs = self.crf_metadata_cls.objects.filter(
            subject_identifier=OuterRef('subject_identifier'),
            visit_code=OuterRef('visit_code'),
            visit_code_sequence=OuterRef('visit_code_sequence'),
            schedule_name=OuterRef('schedule_name'),
            entry_status=REQUIRED).values(
                'subject_identifier', 'visit_code',
                'visit_code_sequence', 'schedule_name').annotate(
                    missing_count=Count('id')).values('missing_count')
        return queryset.annotate(
            missing_crfs_count=Coalesce(
                Subquery(missing_crfs, output_field=IntegerField()), Value(0))
            ).filter(missing_crfs_count__gt=0)

    def get(self, request, *args, **kwargs) -> HttpResponse:

        download_request = request.GET.get('download', None)

        if download_request:

            crf_metadata_list = []

            for visit in self.get_queryset():
                wrapped_visit = self.model_wrapper_cls(visit)
                crf_metadata_objs = wrapped_visit.missing_crfs

                for crf_metadata_obj in crf_metadata_objs:

                    is_off_study = False

                    offstudy_exists = self.caregiver_off_study_cls.objects.filter(
                        subject_identifier=visit.subject_identifier).exists()

                    if offstudy_exists:
                        is_off_study = True

                    temp = dict(
                        subject_identifier=crf_metadata_obj.subject_identifier,
                        visit_code=visit.visit_code,
                        visit_code_sequence=visit.visit_code_sequence,
                        schedule_name=visit.schedule_name,
                        appointment_date=visit.appointment.appt_datetime.date().isoformat(),
                        appointment_status=visit.appointment.appt_status,
                        crf_name=django_apps.get_model(
                            crf_metadata_obj.model)._meta.verbose_name,
                        entry_status=crf_metadata_obj.entry_status,
                        is_off_study=bool(is_off_study),
                        visit_date=visit.report_datetime.date().isoformat()

                    )

                    crf_metadata_list.append(temp)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                f'attachment; filename="missing_crf_{date.today().isoformat()}.csv"')
            df = pd.DataFrame(crf_metadata_list)
            df.to_csv(path_or_buf=response, index=False)

            return response

        return super().get(request, *args, **kwargs)
