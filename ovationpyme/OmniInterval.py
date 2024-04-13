import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as pp
from geospacepy import satplottools
from nasaomnireader.omnireader import omni_interval

from ovationpyme import *

# dt = datetime.datetime(2016, 2, 1, 0, 0, 0)
# tol_hrs_before = 4
# tol_hrs_after = 1
# new_interval_days_before_dt = 1.5
# new_interval_days_after_dt = 1.5
# cadence = '5min'
# startdt = dt - datetime.timedelta(days=new_interval_days_before_dt)
# enddt = dt + datetime.timedelta(days=new_interval_days_after_dt)
# # oi = omni_interval(startdt, enddt, cadence, silent=True)
# df = pd.read_csv('sattelities_data/ACE/ace.csv')
# df["Epoch"] = pd.to_datetime(df["Epoch"])
# df = df[(df['Epoch'] >= startdt) & (df['Epoch'] <= enddt)]
# df['Epoch'] = df['Epoch'].dt.to_pydatetime()


class OmniInterval:
    def __init__(self, df):
        self.cadence = '5min'
        self._data = {
            'Epoch': list(df['Epoch']),
            'cadence': 'hourly',
            'BX_GSE': np.array(df['BX_GSE']),
            'BY_GSM': np.array(df['BY_GSM']),
            'BZ_GSM': np.array(df['BZ_GSM']),
            'proton_density': np.array(df['proton_density']),
            'flow_speed': np.array(df['flow_speed'])
        }

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


# oi = OmniInterval()
#
# atype = 'diff'
# jtype = 'energy'
# estimator = ovation_prime.FluxEstimator(atype, jtype)
# mlatgridN, mltgridN, fluxgridN = estimator.get_flux_for_time(dt, oi, hemi='N')
# mlatgridS, mltgridS, fluxgridS = estimator.get_flux_for_time(dt, oi, hemi='S')
# f = pp.figure(figsize=(11, 5))
# aN = f.add_subplot(121)
# aS = f.add_subplot(122)
#
# XN, YN = satplottools.latlt2cart(mlatgridN.flatten(), mltgridN.flatten(), 'N')
# XS, YS = satplottools.latlt2cart(mlatgridS.flatten(), mltgridS.flatten(), 'S')
#
# XN = XN.reshape(mlatgridN.shape)
# YN = YN.reshape(mltgridN.shape)
# XS = XS.reshape(mlatgridS.shape)
# YS = YS.reshape(mltgridS.shape)
#
# satplottools.draw_dialplot(aN)
# satplottools.draw_dialplot(aS)
#
# mappableN = aN.pcolormesh(XN, YN, fluxgridN, vmin=0, vmax=2)
# mappableS = aS.pcolormesh(XS, YS, fluxgridS, vmin=0, vmax=2)
#
# aN.set_title("Northern Hemisphere Flux")
# aS.set_title("Southern Hemisphere Flux")
#
# f.colorbar(mappableN, ax=aN)
# f.colorbar(mappableS, ax=aS)
#
# f.suptitle("OvationPyme Auroral Model Flux Output at {0} \n AuroralType:{1}, FluxType:{2}".format(dt.strftime('%c'),
#                                                                                                   atype, jtype),
#            fontweight='bold')
# print(f)
