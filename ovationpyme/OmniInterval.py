import datetime
from nasaomnireader.omnireader import omni_interval

import numpy as np

from ovation_utilities import read_solarwind, hourly_solarwind_for_average

dt = datetime.datetime(2023, 9, 1, 12, 10, 0)
tol_hrs_before = 4
tol_hrs_after = 1
new_interval_days_before_dt = 1.5
new_interval_days_after_dt = 1.5
cadence = '5min'
startdt = dt - datetime.timedelta(days=new_interval_days_before_dt)
enddt = dt + datetime.timedelta(days=new_interval_days_after_dt)
oi = omni_interval(startdt, enddt, cadence, silent=True)


class OmniInterval:
    def __init__(self):
        self.cadence = '5min'
        self._data = {
            'Epoch': oi['Epoch'],
            'cadence': 'hourly',
            'BX_GSE': oi['BX_GSE'],
            'BY_GSM': oi['BY_GSM'],
            'BZ_GSM': oi['BZ_GSM'],
            'proton_density': oi['proton_density'],
            'flow_speed': oi['flow_speed']
        }

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


oi = OmniInterval()
print(hourly_solarwind_for_average(dt, oi))


