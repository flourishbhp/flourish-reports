import pytz
from django.apps import apps as django_apps
from edc_metadata.constants import REQUIRED

from ..util import MigrationHelper

tz = pytz.timezone('Africa/Gaborone')


class CRFMetadataModelWrapperMixin:
    crf_metadata_model = 'edc_metadata.crfmetadata'

    @property
    def crf_metadata_cls(self):
        return django_apps.get_model(self.crf_metadata_model)

    @property
    def required_crfs(self):
        crf_metadata = self.crf_metadata_cls.objects.filter(
            subject_identifier=self.object.subject_identifier,
            schedule_name=self.object.schedule_name,
            visit_code=self.object.visit_code,
            visit_code_sequence=self.object.visit_code_sequence,
            entry_status=REQUIRED
        )

        return crf_metadata

    @property
    def missing_crfs_count(self):
        return self.missing_crfs.count()

    @property
    def missing_crfs_names(self):
        crf_names = map(
            lambda crf: django_apps.get_model(crf.model)._meta.verbose_name,
            self.missing_crfs)

        return ', '.join(crf_names)

    @property
    def missing_crfs(self):
        exclude_ids = []

        for metadata_obj in self.required_crfs:
            model_cls = django_apps.get_model(metadata_obj.model)

            migration_helper = MigrationHelper(
                model_cls._meta.app_label, model_cls._meta.model_name)

            date_created = migration_helper.get_model_creation_date()

            visit_report_date = self.object.report_datetime.astimezone(tz).date()

            if (date_created and visit_report_date) and (
                    date_created > visit_report_date):
                exclude_ids.append(metadata_obj.id)

        return self.required_crfs.exclude(id__in=exclude_ids, )
