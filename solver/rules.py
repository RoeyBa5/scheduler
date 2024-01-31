from datetime import timedelta

from solver.models import Shift


def is_night_shift(shift: Shift) -> bool:
    return shift.start_time.hour >= 22 or shift.start_time.hour <= 6


def in_interval(shift: Shift, other_shift: Shift, hours: int) -> bool:
    return timedelta(hours=0) <= shift.end_time - other_shift.start_time <= timedelta(hours=hours) \
        or timedelta(hours=0) <= other_shift.end_time - shift.start_time <= timedelta(hours=hours)


def min_hours_gap_between_shift(shift: Shift, other_shift: Shift) -> bool:
    # make sure there is no overlap between shifts
    if shift.start_time < other_shift.start_time < shift.end_time:
        return False
    if shift.start_time < other_shift.end_time < shift.end_time:
        return False
    # make sure there is at least 4 hours gap between shifts
    return shift.end_time + timedelta(hours=4) <= other_shift.start_time \
        or other_shift.end_time + timedelta(hours=4) <= shift.start_time
