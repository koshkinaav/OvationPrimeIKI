from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm

from OmniInterval import OmniInterval
from visual_test_ovation_prime import draw_weighted_flux

tqdm.pandas()


def get_flux_for_hour(df):
    diff = {
        'type': [],
        'dt': [],
        'fluxN': [],
        'fluxS': []
    }

    mono = {
        'type': [],
        'dt': [],
        'fluxN': [],
        'fluxS': []
    }
    wave = {
        'type': [],
        'dt': [],
        'fluxN': [],
        'fluxS': []
    }
    ions = {
        'type': [],
        'dt': [],
        'fluxN': [],
        'fluxS': []
    }
    df = df.reset_index(drop=True)
    dt = df['Epoch'][0]

    # Преобразование строкового представления в datetime.datetime
    oi = OmniInterval(df)

    for atype, result in zip(['diff', 'mono', 'wave', 'ions'], [diff, mono, wave, ions]):
        js = draw_weighted_flux(dt, oi, atype=atype, jtype='energy', satellite=['ACE'], only_value=True)
        N = js['fluxN']
        S = js['fluxS']
        result['dt'].append(dt)
        result['type'].append(atype)
        result['fluxN'].append(N)
        result['fluxS'].append(S)

    return diff, mono, wave, ions


# def apply_parallel(func, df, num_processes):
#     pool = Pool(num_processes)
#     pool_outputs = tqdm(pool.map(func, df.iterrows()), total=len(df))
#     pool.close()
#     pool.join()
#     return pool_outputs


if __name__ == '__main__':
    Df = pd.read_csv('sattelities_data/DSCOVR/DCOVR.csv')
    Df['Epoch'] = pd.to_datetime(Df['Epoch'])
    Df['Epoch'] = Df['Epoch'].dt.to_pydatetime()
    start_date = min(Df['Epoch'])
    current_date = start_date
    end_date = '2017-01-01'
    Df = Df[(Df.Epoch >= current_date) & (Df.Epoch < end_date)]
    hour_duration = pd.Timedelta(hours=1)
    dataframes = []

    while current_date <= Df.Epoch[len(Df) - 1]:
        current_hour_data = Df[(Df.Epoch >= current_date) & (Df.Epoch < current_date + hour_duration)]
        dataframes.append(current_hour_data)
        current_date += hour_duration

    result = pd.DataFrame()
    print(len(dataframes))

    pool = Pool(processes=2)
    pool_outputs = tqdm(pool.map(get_flux_for_hour, dataframes), total=len(dataframes))
    for outputs in pool_outputs:
        for output in outputs:
            result = pd.concat([result, pd.DataFrame(output)], ignore_index=True)
    result.to_csv('dscovr_forecasts.csv', index=False)
