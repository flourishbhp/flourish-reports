from functools import reduce

from django_pandas.io import read_frame

from flourish_caregiver.models import MaternalDataset, SubjectConsent
from flourish_follow.models import LogEntry, InPersonContactAttempt, WorkList


def merge(lst1, lst2):
    """Return merged list from 2 lists.
    """
    return [a + [b[1]] for (a, b) in zip(lst1, lst2)]


class PrevStudyRecruitmentReportMixin:

    def attempts(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']
        qs = LogEntry.objects.all()
        if prev_study:
            if prev_study == '-----':
                qs = LogEntry.objects.filter(
                    created__range=[start_date, end_date])

            else:
                qs = LogEntry.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date])
        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        qs1 = InPersonContactAttempt.objects.all()
        if prev_study:
            if prev_study == '-----':
                qs1 = InPersonContactAttempt.objects.filter(
                    created__range=[start_date, end_date])
            else:
                qs1 = InPersonContactAttempt.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date])
        df1 = read_frame(qs1, fieldnames=['prev_study', 'study_maternal_identifier'])
        df1 = df1.drop_duplicates(subset=['study_maternal_identifier'])

        result = df.append(df1)
        result = result.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = result[result['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def pending(self, prev_study=None, start_date=None, end_date=None):
        """Return number of participants who are randomised but nothing has been done on them.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']
        qs = WorkList.objects.filter(
            assigned__isnull=False, is_called=False, visited=False)
        if prev_study:
            if prev_study == '-----':
                qs = WorkList.objects.filter(
                    created__range=[start_date, end_date],
                    assigned__isnull=False,
                    is_called=False,
                    visited=False)
            else:
                qs = WorkList.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date],
                    assigned__isnull=False,
                    is_called=False,
                    visited=False)

        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])

        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def unable_to_reach(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        # Call logs
        identifiers = []
        if prev_study:
            if prev_study == '-----':
                identifiers = LogEntry.objects.filter(
                    created__range=[start_date, end_date],
                    phone_num_success=['none_of_the_above']).values_list(
                    'study_maternal_identifier', flat=True)
            else:
                identifiers = LogEntry.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date],
                    phone_num_success=['none_of_the_above']).values_list(
                    'study_maternal_identifier', flat=True)
        identifiers = list(set(identifiers))
        # In contact attempts
        qs = InPersonContactAttempt.objects.filter(
            study_maternal_identifier__in=identifiers,
            successful_location=['none_of_the_above'])
        if prev_study:
            if prev_study == '-----':
                qs = InPersonContactAttempt.objects.filter(
                    study_maternal_identifier__in=identifiers,
                    created__range=[start_date, end_date],
                    successful_location=['none_of_the_above'])
            else:
                qs = InPersonContactAttempt.objects.filter(
                    study_maternal_identifier__in=identifiers,
                    prev_study=prev_study,
                    created__range=[start_date, end_date],
                    successful_location=['none_of_the_above'])
        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def decline_uninterested(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']
        qs = LogEntry.objects.filter(may_call='No')
        if prev_study:
            qs = LogEntry.objects.filter(
                prev_study=prev_study,
                created__range=[start_date, end_date],
                may_call='No')
        elif prev_study == '-----':
            qs = LogEntry.objects.filter(
                created__range=[start_date, end_date],
                may_call='No')
        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def consented(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']

        screening_identifiers = SubjectConsent.objects.all().values_list(
            'screening_identifier', flat=True)
        screening_identifiers = list(set(screening_identifiers))
        qs = MaternalDataset.objects.filter(
            screening_identifier__in=screening_identifiers)
        df = read_frame(qs, fieldnames=['protocol', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = df[df['protocol'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def thinking(self, prev_study=None, start_date=None, end_date=None):
        """Return number of contacted participants.
        """
        prev_studies = [
            'Mpepu',
            'Mma Bana',
            'Mashi',
            'Tshilo Dikotla',
            'Tshipidi']
        qs = LogEntry.objects.filter(appt='thinking')
        if prev_study:
            if prev_study == '-----':
                qs = LogEntry.objects.filter(
                    created__range=[start_date, end_date],
                    appt='thinking')
            else:
                qs = LogEntry.objects.filter(
                    prev_study=prev_study,
                    created__range=[start_date, end_date],
                    appt='thinking')
        df = read_frame(qs, fieldnames=['prev_study', 'study_maternal_identifier'])
        df = df.drop_duplicates(subset=['study_maternal_identifier'])

        prev_study_list = []
        for prev_study in prev_studies:
            df_prev = df[df['prev_study'] == prev_study]
            prev_study_list.append([prev_study, df_prev[df_prev.columns[0]].count()])
        return prev_study_list

    def prev_report_data(self, prev_study=None, start_date=None, end_date=None):
        """Return the data for the report.
        """
        data = []
        if prev_study and start_date and end_date:
            data = [
                self.attempts(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.pending(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.unable_to_reach(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.decline_uninterested(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.thinking(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date),
                self.consented(
                    prev_study=prev_study,
                    start_date=start_date,
                    end_date=end_date)]
        else:
            data = [
                self.attempts(), self.pending(), self.unable_to_reach(),
                self.decline_uninterested(), self.thinking(), self.consented()]
        result = reduce(merge, data)
        return result
