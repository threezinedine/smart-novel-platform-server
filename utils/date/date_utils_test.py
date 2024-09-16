from datetime import timedelta
import unittest
from .date_utils import *


class DateUtilsTest(unittest.TestCase):
    def test_CheckGapWeek(self):
        today = date.today()
        assert CheckNumberGapWeek(today, today) == 0

        # get next monday
        nextMon = date.today()

        while nextMon.strftime("%a") != "Mon" or nextMon == today:
            nextMon += timedelta(days=1)

        assert CheckNumberGapWeek(today, nextMon) == 1

        yesterday = today - timedelta(days=1)
        assert CheckNumberGapWeek(today, yesterday) == -1

        assert CheckNumberGapWeek(today, today) == 0
