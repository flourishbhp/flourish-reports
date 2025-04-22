from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from .missing_crf_listview_mixin import MissingCRFListViewMixin
from .filters import MissingListboardViewFilters
from ...model_wrappers import ChildVisitModelWrapper


class ChildMissingCrfListView(NavbarViewMixin,
                              EdcBaseViewMixin,
                              ListboardFilterViewMixin,
                              MissingCRFListViewMixin,
                              ListboardView):

    listboard_template = 'missing_crf_listboard_template'
    listboard_url = 'child_missing_crf_report_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = 'far fa-user-circle'
    listboard_view_filters = MissingListboardViewFilters()

    model = 'flourish_child.childvisit'
    model_wrapper_cls = ChildVisitModelWrapper
    navbar_name = 'flourish_reports'
    navbar_selected_item = 'missing_crf_report'
