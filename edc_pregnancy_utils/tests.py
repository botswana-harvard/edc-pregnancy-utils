import unittest

from datetime import datetime

from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow

from .constants import ULTRASOUND, LMP
from .edd import Edd
from .ga import Ga
from .lmp import Lmp
from .ultrasound import Ultrasound


class TestPregnancyUtils(unittest.TestCase):

    def test_lmp_none(self):
        """Assert Lmp handles None."""
        lmp = Lmp()
        self.assertIsNone(lmp.edd)

    def test_lmp_edd(self):
        """Assert Lmp return edd."""
        dt = get_utcnow()
        edd = datetime.fromordinal((dt + relativedelta(days=280)).toordinal())
        self.assertEqual(edd, Lmp(lmp=dt).edd)

    def test_lmp_ga(self):
        """Assert Lmp return edd."""
        dt = get_utcnow().date()
        lmp = Lmp(lmp=dt - relativedelta(weeks=25), reference_date=dt)
        self.assertEqual(lmp.ga.weeks, 15)

    def test_ultrasound_days_boundaries(self):
        """Assert Ultrasound raises errors for invalid days."""
        dt = get_utcnow()
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=1, ga_days=7)
            self.fail('TypeError not raised!')
        except TypeError:
            pass

        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=1, ga_days=-1)
            self.fail('TypeError not raised!')
        except TypeError:
            pass

    def test_ultrasound_weeks_boundaries(self):
        """Assert Ultrasound raises errors for invalid weeks."""
        dt = get_utcnow()
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=-1)
            self.fail('TypeError not raised!')
        except TypeError:
            pass
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=0)
            self.fail('TypeError not raised!')
        except TypeError:
            pass
        try:
            Ultrasound(ultrasound_date=dt, ga_weeks=40)
            self.fail('TypeError not raised!')
        except TypeError:
            pass

    def test_ultrasound_weeks_floor(self):
        """Assert ga weeks is rounded down to nearest int."""
        dt = get_utcnow()
        for week in range(1, 40):
            for day in range(0, 7):
                ultrasound = Ultrasound(ultrasound_date=dt, ga_weeks=week, ga_days=day)
                self.assertEqual(week, ultrasound.ga.weeks)

    def test_ultrasound_ga(self):
        """Assert Ultrasound returns ga in weeks, as is."""
        dt = get_utcnow()
        ultrasound = Ultrasound(ultrasound_date=dt, ga_weeks=25, ga_days=3)
        self.assertEqual(ultrasound.ga.weeks, 25)

    def test_ultrasound_edd(self):
        """Assert Ultrasound returns edd as future date."""
        dt = get_utcnow()
        for week in range(1, 40):
            for day in range(0, 7):
                ultrasound = Ultrasound(ultrasound_date=dt, ga_weeks=week, ga_days=day)
                self.assertGreater(ultrasound.edd, dt)

    def test_edd_none(self):
        """Assert Edd can handle nulls."""
        lmp = Lmp()
        ultrasound = Ultrasound()
        edd = Edd(lmp=lmp, ultrasound=ultrasound)
        self.assertIsNone(edd.edd)
        edd = Edd(lmp=None, ultrasound=None)
        self.assertIsNone(edd.edd)
        edd = Edd()
        self.assertIsNone(edd.edd)

    def test_ultrasound_none(self):
        """Assert Ultrasound can handle nulls."""
        ultrasound = Ultrasound()
        self.assertIsNone(ultrasound.ga)
        self.assertIsNone(ultrasound.edd)
        ultrasound = Ultrasound(None, 25, 3)
        self.assertIsNone(ultrasound.ga)
        self.assertIsNone(ultrasound.edd)

    def test_edd_without_ultrasound(self):
        """Assert Edd chooses Lmp.edd if Utrasound is null."""
        dt = get_utcnow()
        lmp = Lmp(lmp=dt - (relativedelta(weeks=25) + relativedelta(days=3)))
        ultrasound = Ultrasound(None, 25, 3)
        edd = Edd(lmp, ultrasound)
        self.assertEqual(edd.edd, lmp.edd)
        self.assertEqual(edd.method, LMP)

    def test_edd_without_lmp(self):
        """Assert Edd chooses Ultrasound.edd if Lmp is null."""
        ultrasound_dt = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        edd = Edd(lmp, ultrasound)
        self.assertEqual(edd.edd, ultrasound.edd)
        self.assertEqual(edd.method, ULTRASOUND)

    def test_ga_without_lmp_uses_ultrasound(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        ultrasound_dt = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.ga, ultrasound.ga)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_without_ultrasound_uses_lmp(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        dt = get_utcnow()
        lmp = Lmp(lmp=dt - (relativedelta(weeks=25) + relativedelta(days=3)))
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, lmp.ga.weeks)
        self.assertEqual(ga.method, LMP)

    def test_ga_without_lmp_without_ultrasound_is_none(self):
        """Assert Ga null of no lmp and no ultrasound."""
        lmp = Lmp()
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.ga, None)
        self.assertEqual(ga.method, None)

    def test_ga_weeks_from_lmp(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        dt = get_utcnow()
        lmp = dt - (relativedelta(weeks=25) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp, reference_date=dt)
        ultrasound = Ultrasound()
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 15)
        self.assertEqual(ga.method, LMP)

    def test_ga_weeks_from_ultrasound(self):
        """Assert Ga chooses Ultrasound.ga if Lmp is null."""
        ultrasound_dt = get_utcnow()
        lmp = Lmp()
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 25)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_weeks_from_ultrasound_if_both(self):
        """Assert Ga chooses Ultrasound.ga if both Lmp and Ultrasound provided."""
        ultrasound_dt = get_utcnow()
        lmp_dt = get_utcnow() - (relativedelta(weeks=23) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp_dt)
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound)
        self.assertEqual(ga.weeks, 25)
        self.assertEqual(ga.method, ULTRASOUND)

    def test_ga_weeks_from_lmp_if_both_and_pref_lmp(self):
        """Assert Ga chooses Lmp.ga if both Lmp and Ultrasound provided but prefer_ultrasound=False."""
        ultrasound_dt = get_utcnow()
        lmp_dt = get_utcnow() - (relativedelta(weeks=23) + relativedelta(days=3))
        lmp = Lmp(lmp=lmp_dt)
        ultrasound = Ultrasound(ultrasound_dt, ga_weeks=25)
        ga = Ga(lmp, ultrasound, prefer_ultrasound=False)
        self.assertEqual(ga.weeks, 17)
        self.assertEqual(ga.method, LMP)
