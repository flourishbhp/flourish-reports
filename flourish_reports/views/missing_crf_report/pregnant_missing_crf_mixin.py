from edc_appointment.models import Appointment as CaregiverAppointment
from flourish_caregiver.models import *
from edc_appointment.constants import *
from edc_appointment.models import Appointment as CaregiverAppointment
from flourish_visit_schedule.visit_schedules.crfs.caregiver_crfs import *
from django.apps import apps as django_apps
from edc_metadata.constants import REQUIRED
from edc_metadata.models import CrfMetadata


class PregnantMissingCrfMixin:

    def preg_screening(self):
        # Screening stats
        screen_screening_identifiers = ScreeningPregWomenInline.objects.filter(
            is_eligible=True).values_list('mother_screening__screening_identifier', flat=True)

        consent_screening_identifiers = SubjectConsent.objects.values_list(
            'screening_identifier', flat=True)

        prior_screening_identifiers = ScreeningPriorBhpParticipants.objects.values_list(
            'screening_identifier', flat=True)

        subject_identifiers = (set(screen_screening_identifiers) ^ set(
            consent_screening_identifiers)) - set(prior_screening_identifiers)

        return {
            'title': 'Screening',
            'count': len(subject_identifiers),
            'subject_identifiers': subject_identifiers
        }

    def missing_locators_statistics(self):
        # Locator
        locator_subject_identifiers = CaregiverLocator.objects.values_list(
            'subject_identifier', flat=True)

        consent_subject_identifiers = SubjectConsent.objects.values_list(
            'subject_identifier', flat=True)

        subject_identifiers = set(locator_subject_identifiers) ^ set(
            consent_subject_identifiers)

        return {
            'title': 'Locators',
            'count': len(subject_identifiers),
            'subject_identifiers': subject_identifiers
        }

    def missing_antenatal_statistics(self):
        # Antenatal
        consent_subject_identifiers = CaregiverChildConsent.objects.filter(
            study_child_identifier__isnull=True).values_list('subject_consent__subject_identifier', flat=True)

        antenatal_subject_identifiers = AntenatalEnrollment.objects.values_list(
            'subject_identifier', flat=True)

        subject_identifiers = set(consent_subject_identifiers) ^ set(
            antenatal_subject_identifiers)

        return {
            'title': 'Antenatal',
            'count': len(subject_identifiers),
            'subject_identifiers': subject_identifiers
        }

    def crf_statistics(self, appt_status, visit_code):

        antenental_statistics = dict()
        crf_collections = list()

        if visit_code == '1000M':
            crf_collections = a_crf_2000.forms
        elif visit_code == '2000D':
            crf_collections = crf_2000d.forms
        else:
            crf_collections = crf_2001.forms

        for form in crf_collections:
            model_cls = django_apps.get_model(form.model)

            appt_pids = CaregiverAppointment.objects.filter(
                appt_status=appt_status,
                visit_code=visit_code,).values_list('subject_identifier', flat=True)

            crf_metadata_objs = CrfMetadata.objects.filter(
                model=form.model,
                entry_status=REQUIRED,
                visit_code=visit_code,
                subject_identifier__in=appt_pids
            )

            antenental_statistics[model_cls._meta.verbose_name] = crf_metadata_objs.count()
        return antenental_statistics
