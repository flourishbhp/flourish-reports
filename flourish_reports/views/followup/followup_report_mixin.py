from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.db.models import Q
from django.db.models.aggregates import Count
from django.db.models.expressions import OuterRef, Exists, Subquery

from edc_base.utils import get_utcnow
from flourish_child.helper_classes.utils import child_utils


class FollowupReportMixin:

    cohort_model = 'flourish_caregiver.cohort'
    cohortschedules_model = 'flourish_caregiver.cohortschedules'
    child_visit_model = 'flourish_child.childvisit'
    child_offstudy_model = 'flourish_prn.childoffstudy'

    @property
    def year_3_date(self):
        app_config = django_apps.get_app_config('edc_protocol')
        study_open_dt = app_config.study_open_datetime
        return (study_open_dt + relativedelta(years=3)).date()

    @property
    def cohort_model_cls(self):
        return django_apps.get_model(self.cohort_model)

    @property
    def cohortschedules_model_cls(self):
        return django_apps.get_model(self.cohortschedules_model)

    @property
    def child_visit_model_cls(self):
        return django_apps.get_model(self.child_visit_model)

    @property
    def child_offstudy_model_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def child_offstudy_sidx(self):
        return self.child_offstudy_model_cls.objects.values_list(
            'subject_identifier', flat=True)

    @property
    def child_cohort_instances(self):
        cohort_instances = self.cohort_model_cls.objects.exclude(
            Q(subject_identifier__in=self.child_offstudy_sidx) | Q(name__icontains='sec'))
        return cohort_instances

    @property
    def unique_cohort_instances(self):
        latest_instances = self.cohort_model_cls.objects.exclude(
            Q(subject_identifier__in=self.child_offstudy_sidx) | Q(name__icontains='sec')).filter(
                subject_identifier=OuterRef('subject_identifier')).order_by('assign_datetime').values('id')[:1]

        cohort_instances = self.cohort_model_cls.objects.filter(id=Subquery(latest_instances))
        return cohort_instances

    def parse_to_set(self, data=[]):
        return [(row.get('subject_identifier'), row.get('name'), row.get('enrollment_date')) for row in data]

    def expected_fus(self, records={}):
        expected_fu = []
        for child_cohort in self.unique_cohort_instances:
            subject_identifier = child_cohort.subject_identifier
            cohort_name = child_cohort.name
            child_age = child_cohort.child_age
            enrollment_dt = child_cohort.caregiver_child_consent.consent_datetime.date()

            expected_fu.append(
                {'subject_identifier': subject_identifier,
                 'name': cohort_name,
                 'child_age': child_age,
                 'enrollment_cohort': child_cohort.enrollment_cohort,
                 'enrollment_date': enrollment_dt})
        records.update({'expected_fus': expected_fu})
        return expected_fu

    def due_for_fus(self, records={}):
        due_fu = []
        expected_fus = records.get('expected_fus')
        for child_cohort in expected_fus:
            expected = True
            enrollment_dt = child_cohort.get('enrollment_date')
            if child_cohort.get('enrollment_cohort') and enrollment_dt >= self.year_3_date:
                # Check if a year after enrollment has passed.
                onsch_delta = (get_utcnow().date() - enrollment_dt).days
                expected = onsch_delta / 365 >= 1
            elif not child_cohort.get('enrollment_cohort'):
                expected = self.sq_enrolled_expected(
                    child_cohort.get('name'), child_cohort.get('child_age'))

            if expected:
                due_fu.append(child_cohort)
        records.update({'due_fus': due_fu})

    def sq_enrolled_expected(self, cohort_name, child_age):
        cohort_limits = {'cohort_b': 7, 'cohort_c': 12}
        if child_age >= cohort_limits.get(cohort_name):
            return True
        return False

    @property
    def sq_enrolled_sidxs(self):
        sq_enrolled = self.child_cohort_instances.values(
            'subject_identifier').annotate(
                cohort_count=Count('subject_identifier')).filter(
                    cohort_count__gt=1).values_list('subject_identifier', flat=True)
        return sq_enrolled

    @property
    def not_sq_enrolled(self):
        return self.child_cohort_instances.exclude(
            subject_identifier__in=self.sq_enrolled_sidxs)

    def get_fu_schedule_name(self, cohort_name):
        """ Query to get the schedule_name for a corresponding
            cohort_name attr.
        """
        schedule_names = self.cohortschedules_model_cls.objects.filter(
            cohort_name=cohort_name,
            onschedule_model__startswith='flourish_child',
            schedule_type__in=['followup', 'sq_followup']).values_list('schedule_name', flat=True)

        return schedule_names

    def get_fu_visit(self, subject_identifier, schedule_names):
        visit = self.child_visit_model_cls.objects.filter(
                subject_identifier=subject_identifier,
                schedule_name__in=schedule_names)
        return visit

    def get_cohort_details(self, cohort_dict):
        """ Returns subject_identifier, cohort_name from a cohort instance dictionary
            @param cohort_dict: dictionary of a cohort model instance
            @return: tuple (subject_identifier, cohort_name)
        """
        subject_identifier = cohort_dict.get('subject_identifier', '')
        cohort_name = cohort_dict.get('name', '')
        return subject_identifier, cohort_name

    def completed_fus(self, records={}):
        has_fu = []
        expected_fus = records.get('expected_fus')
        for child_cohort in expected_fus:
            subject_identifier = child_cohort.get('subject_identifier')
            cohort_name = child_cohort.get('name')
            child_age = child_cohort.get('child_age')
            cohort_sch_names = self.get_fu_schedule_name(cohort_name)

            visit = self.get_fu_visit(subject_identifier, cohort_sch_names)
            if visit.exists():
                has_fu.append(
                    {'subject_identifier': subject_identifier,
                     'name': cohort_name,
                     'enrollment_date': child_cohort.get('enrollment_date'),
                     'fu_visit_date': visit.last().report_datetime.date(),
                     'child_age': child_age})
        records.update({'completed_fus': has_fu})
        return has_fu

    def incomplete_fus(self, records={}):
        expected_fus = records.get('expected_fus')
        completed_fus = records.get('completed_fus')
        has_fus = self.parse_to_set(completed_fus)
        expected_fus = self.parse_to_set(expected_fus)
        no_fus = set(expected_fus) - set(has_fus)
        records.update({'incomplete_fus': no_fus})
        return no_fus

    def sq_enrolled_before_fu(self, records={}):
        enrolled_before = []
        for sidx in self.sq_enrolled_sidxs:
            cohorts = self.child_cohort_instances.filter(subject_identifier=sidx,)
            enrol_cohort = cohorts.filter(enrollment_cohort=True).first()
            curr_cohort = cohorts.exclude(enrollment_cohort=True).order_by('assign_datetime').last()

            schedule_names = self.get_fu_schedule_name(enrol_cohort.name)
            if not self.get_fu_visit(sidx, schedule_names).exists():
                enrolled_before.append({'subject_identifier': sidx,
                                        'enrol_cohort': enrol_cohort.name,
                                        'current_cohort': curr_cohort.name })
        records.update({'sq_enrolled_before_fu': enrolled_before})
        return enrolled_before

    def upcoming_scheduled(self, records={}):
        scheduled_records = []
        subquery = child_utils.participant_note_model_cls.objects.filter(
            subject_identifier=OuterRef('subject_identifier'),
            title='Follow Up Schedule',
            date__gte=get_utcnow().date())
        scheduled = self.child_cohort_instances.annotate(
            is_scheduled=Exists(subquery)).filter(current_cohort=True, is_scheduled=True).values(
                'subject_identifier', 'name', )

        for row in scheduled:
            scheduled_dt = child_utils.get_child_fu_schedule(row.get('subject_identifier')).date
            row.update(scheduled_date=scheduled_dt)
            scheduled_records.append(row)
        records.update({'upcoming_scheduled': scheduled_records})
        return scheduled_records
