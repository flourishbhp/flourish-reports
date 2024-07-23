from django.apps import apps as django_apps


class ReportsViewMixin:

    cohort_model = 'flourish_caregiver.cohort'
    cohortschedules_model = 'flourish_caregiver.cohortschedules'
    child_visit_model = 'flourish_child.childvisit'
    child_offstudy_model = 'flourish_prn.childoffstudy'

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
            subject_identifier__in=self.child_offstudy_sidx)
        return cohort_instances

    @property
    def primary_cohort_instances(self):
        return self.child_cohort_instances.exclude(
            name__icontains='sec')

    def get_cohorts(self, enroll=False):
        if enroll:
            return self.child_cohort_instances.filter(enrollment_cohort=True)
        else:
            return self.child_cohort_instances

    @property
    def latest_primary_cohort_instances(self):
        sidxs = self.primary_cohort_instances.values_list(
            'subject_identifier', flat=True)
        sidxs = list(set(sidxs))
        instances = []
        for sidx in sidxs:
            latest_instance = self.primary_cohort_instances.filter(
                subject_identifier=sidx).latest('assign_datetime')
            instances.append(latest_instance)
        return instances

    @property
    def current_primary_cohort_instances(self):
        current_instances = self.primary_cohort_instances.filter(
            current_cohort=True)
        sidxs = current_instances.values_list(
            'subject_identifier', flat=True)
        sidxs = list(set(sidxs))
        instances = []
        for sidx in sidxs:
            latest_instance = current_instances.filter(
                subject_identifier=sidx).latest('assign_datetime')
            instances.append(latest_instance)
        return instances
