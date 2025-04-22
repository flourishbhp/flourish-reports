from django.conf import settings
from edc_model_wrapper.wrappers import ModelWrapper

from .crfmetadata_model_wrapper_mixin import CRFMetadataModelWrapperMixin


class MaternalVisitModelWrapper(CRFMetadataModelWrapperMixin,
                                ModelWrapper):
    model = 'flourish_caregiver.maternalvisit'
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    next_url_attrs = ['subject_identifier', 'appointment']
