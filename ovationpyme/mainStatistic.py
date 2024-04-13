import pandas as pd
from  visual_test_ovation_prime import draw_weighted_flux
from OmniInterval import OmniInterval
from tqdm import tqdm


df = pd.read_csv('sattelities_data/ACE/ACE.csv')
df['Epoch'] = pd.to_datetime(df['Epoch'])
df['Epoch'] = df['Epoch'].dt.to_pydatetime()

diff = {
    'fluxN': [],
    'fluxS': []
}

mono = {
    'fluxN': [],
    'fluxS': []
}
wave = {
    'fluxN': [],
    'fluxS': []
}
ions = {
    'fluxN': [],
    'fluxS': []
}
for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    i = 0
    dt = row['Epoch']
    r = pd.DataFrame([row])
    oi = OmniInterval(r)
    flag= False

    for atype, result in zip(['diff', 'mono', 'wave', 'ions'], [diff, mono, wave, ions]):
        js = draw_weighted_flux(dt, oi, atype=atype, jtype='energy', satellite=['ACE'], only_value=True)
        N = js['fluxN']
        S = js['fluxS']
        result['fluxN'].append(N)
        result['fluxS'].append(S)
        i += 1
        if i == 10:
            flag = True
            break

    if flag:
        break

print(diff, mono, wave, ions)
