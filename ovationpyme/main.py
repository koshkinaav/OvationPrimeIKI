import io
import logging
import sys
import datetime
import pandas as pd
from OmniInterval import OmniInterval
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, send_file
from geospacepy import special_datetime

import ovation_utilities
from ovationpyme.visual_test_ovation_prime import draw_weighted_flux, draw_seasonal_flux, draw_conductance

tol_hrs_before = 4
tol_hrs_after = 1
new_interval_days_before_dt = 1.5
new_interval_days_after_dt = 1.5
cadence = '5min'


app = Flask(__name__)

log_file = 'ovation_prime_output.log'
sys.stdout = open(log_file, 'w')


# http://localhost:5000/api/v1/draw_weighted_flux?dt=2023-11-28T10:00:00&atype=diff&jtype=energy
# http://localhost:5000/api/v1/draw_seasonal_flux?seasonN=winter&seasonS=summer&atype=diff&jtype=energy
# http://localhost:5000/api/v1/draw_conductance?dt=2023-11-28T10:00:00&hemi=N
# http://localhost:5000/api/v1/draw_weighted_flux?dt=2018-01-01T10:00:00&only_value=true&atype=diff&jtype=energy&satellite=WIND

@app.route('/api/v1/draw_weighted_flux', methods=['GET'])
def weighted_flux():

    dt = request.args.get('dt')
    atype = request.args.get('atype')
    jtype = request.args.get('jtype')
    satellite = request.args.get('satellite')
    only_value = request.args.get('only_value')
    if only_value == 'true':
        only_value = True
    elif only_value == 'false':
        only_value = False
    else:
        jsonify({'Invalid value for atype parameter. Allowed values: true, false'})


    # Проверка обязательности всех параметров
    missing_params = []
    param_formats = {
        'dt': 'yyyy-mm-ddThh:mm:ss',
        'atype': 'str, one of [diff, mono, wave, ions]',
        'jtype': 'str, one of [energy, number]',
        'satellite': 'str, one of [ACE, DSCOVR, WIND]'
    }

    if not dt:
        missing_params.append('dt')
    if not atype:
        missing_params.append('atype')
    if not jtype:
        missing_params.append('jtype')
    if not satellite:
        missing_params.append('satellite')

    if len(missing_params) > 0:
        error_message = 'Missing required parameters: '
        error_message += ', '.join(missing_params)
        error_formats = [f"{param} - {param_formats[param]}" for param in missing_params]
        error_message += "; "
        error_message += "; ".join(error_formats)
        return jsonify({'error': error_message}), 400

    # Проверка условия для параметра atype
    if atype not in ['diff', 'mono', 'wave', 'ions']:
        return jsonify({'error': f'Invalid value for atype parameter. Allowed values: diff, mono, wave, ions'}), 400

    # Проверка условия для параметра jtype
    if jtype not in ['energy', 'number']:
        return jsonify({'error': f'Invalid value for jtype parameter. Allowed values: energy, number'}), 400

    if satellite not in ['ACE', 'DSCOVR', 'WIND']:
        return jsonify({'error': f'Invalid value for satellite parameter. Allowed values: ACE, DSCOVR, WIND'}), 400

    try:
        parsed_dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        hour = parsed_dt.hour
        minutes = parsed_dt.minute
        seconds = parsed_dt.second
        dt = datetime.datetime(parsed_dt.year, parsed_dt.month, parsed_dt.day, hour, minutes, seconds)
    except ValueError:
        return jsonify({'error': f'Invalid format for dt parameter. Expected format: 2023-03-02T10:00:00'}), 400

    satellite_data = pd.read_csv(f'sattelities_data/{satellite}/{satellite}.csv')
    available_dates = list(satellite_data.Epoch.astype('str').unique())
    startdt = dt - datetime.timedelta(days=new_interval_days_before_dt)
    enddt = dt + datetime.timedelta(days=new_interval_days_after_dt)
    satellite_data["Epoch"] = pd.to_datetime(satellite_data["Epoch"])
    satellite_data = satellite_data[(satellite_data['Epoch'] >= startdt) & (satellite_data['Epoch'] <= enddt)]
    satellite_data['Epoch'] = satellite_data['Epoch'].dt.to_pydatetime()
    if len(satellite_data) == 0:
        return jsonify({'error': f'There is no data for {dt}. Available dates are {available_dates}'}), 400
    oi = OmniInterval(satellite_data)
    if only_value:
        response = draw_weighted_flux(dt, oi,  atype=atype, jtype=jtype, satellite=satellite, only_value=only_value)
        return jsonify(str(response))
    else:
        f = draw_weighted_flux(dt, oi,  atype=atype, jtype=jtype, satellite=satellite, only_value=only_value)
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close(f)
    # Возвращение графика как ответ на запрос
    return send_file(image_stream, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=False)
