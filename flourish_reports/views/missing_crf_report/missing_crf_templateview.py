from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.apps import apps as django_apps
from edc_appointment.constants import *
from edc_metadata.constants import REQUIRED, NOT_REQUIRED, KEYED
from collections import Counter
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from .pregnant_missing_crf_mixin import PregnantMissingCrfMixin


class MissingCrfTemplateView(EdcBaseViewMixin,
                             NavbarViewMixin, PregnantMissingCrfMixin, TemplateView):
    template_name = 'flourish_reports/missing_crfs/missing_crf_templateview.html'
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crf_dashboard'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data['preg_screening'] = self.preg_screening()
        context_data['missing_locators_statistics'] = self.missing_locators_statistics()
        context_data['missing_antenatal_statistics'] = self.missing_antenatal_statistics()
        context_data['antenental_completed_appt_statistics'] = self.crf_statistics(
            COMPLETE_APPT, '1000M')
        context_data['antenental_incomplete_appt_statistics'] = self.crf_statistics(
            INCOMPLETE_APPT, '1000M')

        context_data['birth_completed_appt_statistics'] = self.crf_statistics(
            COMPLETE_APPT, '2000D')

        context_data['birth_incomplete_appt_statistics'] = self.crf_statistics(
            INCOMPLETE_APPT, '2000D')

        return context_data
