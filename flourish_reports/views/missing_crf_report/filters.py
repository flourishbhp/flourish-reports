from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters
from edc_appointment.constants import COMPLETE_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT

"""
    CANCELLED_APPT = 'cancelled'
    COMPLETE_APPT = 'done'
    INCOMPLETE_APPT = 'incomplete'
    IN_PROGRESS_APPT = 'in_progress'
    NEW_APPT = 'new'
"""


class MissingListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        label='All',
        position=1,
        lookup={})

    completed_appt = ListboardFilter(
        label='Complete Appointments',
        position=2,
        lookup={'appointment__appt_status': COMPLETE_APPT})

    incompleted_appt = ListboardFilter(
        label='Incomplete Appointments',
        position=3,
        lookup={'appointment__appt_status': INCOMPLETE_APPT})

    inprogress_appt = ListboardFilter(
        label='In Progress Appointments',
        position=4,
        lookup={'appointment__appt_status': IN_PROGRESS_APPT})

    cancelled_appt = ListboardFilter(
        label='Cancelled Appointments',
        position=5,
        lookup={'appointment__appt_status': CANCELLED_APPT}
    )
