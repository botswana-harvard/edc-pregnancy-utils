from datetime import date
from dateutil.relativedelta import relativedelta

from .constants import ULTRASOUND, LMP
from .lmp import Lmp
from .ultrasound import Ultrasound


class Edd:

    def __init__(self, lmp=None, ultrasound=None):
        """Returns an instance with the "confirmed" edd and the method of confirmation."""
        self.edd = None
        self.method = None
        self.diffdays = None
        self.lmp = lmp or Lmp()
        self.ultrasound = ultrasound or Ultrasound()
        try:
            self.edd, self.method, self.diffdays = self.get_edd()
        except TypeError:
            if self.lmp.edd:
                self.edd = self.lmp.edd
                self.method = LMP
            elif self.ultrasound.edd:
                self.edd = self.ultrasound.edd
                self.method = ULTRASOUND
        try:
            self.edd = self.edd.date()
        except AttributeError:
            pass

    def get_edd(self):
        edd = None
        method = None
        diffdays = abs((self.lmp.edd - self.ultrasound.edd).days)
        dt = date.today()
        if dt + relativedelta(weeks=16) <= dt + self.lmp.ga <= dt + (relativedelta(weeks=21) + relativedelta(days=6)):
            if 0 <= diffdays <= 10:
                edd = self.lmp.edd
                method = LMP
            elif 10 < diffdays:
                edd = self.ultrasound.edd
                method = ULTRASOUND
        elif (dt + (relativedelta(weeks=21) + relativedelta(days=6)) < dt + self.lmp.ga <=
                dt + (relativedelta(weeks=27) + relativedelta(days=6))):
            if 0 <= diffdays <= 14:
                edd = self.lmp.edd
                method = LMP
            elif 14 < diffdays:
                edd = self.ultrasound.edd
                method = ULTRASOUND
        elif dt + (relativedelta(weeks=27) + relativedelta(days=6)) < dt + self.lmp.ga:
            if 0 <= diffdays <= 21:
                edd = self.lmp.edd
                method = LMP
            elif 21 < diffdays:
                edd = self.ultrasound.edd
                method = ULTRASOUND
        return edd, method, diffdays if edd else None
