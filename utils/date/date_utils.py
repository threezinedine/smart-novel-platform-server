from datetime import date, timedelta


def CheckNumberGapWeek(
    start_date: date,
    checked_date: date,
) -> int:
    """
    Gap week is the number of weeks between two dates
        but just care about the number of full weeks
        and the week that the checked_date is in.

    Args:
        start_date: The date when its week is the
            reference for the checked_date to calculate
            the gap week, the remaining days of the week
            of the start_date are not counted.

        checked_date: The date to calculate the gap week
            from the start_date.

    Returns:
        `1` if the checked_date < start_date
        `0` if the checked_date is in the same week as the start_date
            (but later than the start_date)
        `n` if the checked_date is n weeks after the start

    Example:
        Mon  Tue  Wed  Thu  Fri  Sat  Sun
        1    2    3    4    5    6    7
        8    9   10   11   12   13   14
        15  16   17   18   19   20   21
        22  23   24   25   26   27   28
        29  30

        start = 5, checked = 2, gap = -1
        start = 5, checked = 5, gap = 0
        start = 5, checked = 6, gap = 0
        start = 5, checked = 12, gap = 1
        start = 5, checked = 15, gap = 2
        start = 5, checked = 16, gap = 2
        start = 5, checked = 29, gap = 4
    """
    # get nearest monday (not include today)
    nextMon = start_date

    while nextMon.strftime("%a") != "Mon" or nextMon == start_date:
        nextMon += timedelta(days=1)

    if checked_date < start_date:
        return -1

    delta = checked_date - nextMon
    if delta.days < 0:
        return 0

    return delta.days // 7 + 1
