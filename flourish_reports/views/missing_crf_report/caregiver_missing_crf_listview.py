from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from .missing_crf_listview_mixin import MissingCRFListViewMixin
from .filters import MissingListboardViewFilters
from ...model_wrappers import MaternalVisitModelWrapper


class CaregiverMissingCrfListView(NavbarViewMixin,
                                  EdcBaseViewMixin,
                                  ListboardFilterViewMixin,
                                  MissingCRFListViewMixin,
                                  ListboardView):

    listboard_template = 'missing_crf_listboard_template'
    listboard_url = 'missing_crf_report_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = 'far fa-user-circle'
    listboard_view_filters = MissingListboardViewFilters()

    model = 'flourish_caregiver.maternalvisit'
    model_wrapper_cls = MaternalVisitModelWrapper
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crf_report'

