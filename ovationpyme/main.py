import io
import sys
from datetime import datetime

import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, send_file
from geospacepy import special_datetime

import ovation_utilities
from ovationpyme.visual_test_ovation_prime import draw_weighted_flux, draw_seasonal_flux, draw_conductance

app = Flask(__name__)

log_file = 'ovation_prime_output.log'
sys.stdout = open(log_file, 'w')


# http://localhost:5000/api/v1/draw_weighted_flux?dt=2023-11-28T10:00:00&atype=diff&jtype=energy
# http://localhost:5000/api/v1/draw_seasonal_flux?seasonN=winter&seasonS=summer&atype=diff&jtype=energy
# http://localhost:5000/api/v1/draw_conductance?dt=2023-11-28T10:00:00&hemi=N
# http://127.0.0.1:5000/api/v1/solar_wind_data?dt=2022-11-30T00:00:00

@app.route('/api/v1/draw_weighted_flux', methods=['GET'])
def weighted_flux():
    dt = request.args.get('dt')
    atype = request.args.get('atype')
    jtype = request.args.get('jtype')

    # Проверка обязательности всех параметров
    missing_params = []
    param_formats = {
        'dt': 'yyyy-mm-ddThh:mm:ss',
        'atype': 'str, one of [diff, mono, wave, ions]',
        'jtype': 'str, one of [energy, number]'
    }

    if not dt:
        missing_params.append('dt')
    if not atype:
        missing_params.append('atype')
    if not jtype:
        missing_params.append('jtype')

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

    try:
        parsed_dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        hour = parsed_dt.hour
        minutes = parsed_dt.minute
        seconds = parsed_dt.second
        dt = datetime(parsed_dt.year, parsed_dt.month, parsed_dt.day, hour, minutes, seconds)
    except ValueError:
        return jsonify({'error': f'Invalid format for dt parameter. Expected format: 2023-03-02T10:00:00'}), 400

    f = draw_weighted_flux(dt, atype=atype, jtype=jtype)
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close(f)
    # Возвращение графика как ответ на запрос
    return send_file(image_stream, mimetype='image/png')


@app.route('/api/v1/draw_seasonal_flux', methods=['GET'])
def seasonal_flux():
    seasonN = request.args.get('seasonN')
    seasonS = request.args.get('seasonS')
    atype = request.args.get('atype')
    jtype = request.args.get('jtype')
    # Проверка обязательности всех параметров
    missing_params = []
    param_formats = {
        'seasonN': 'str, one of [winter, spring, summer, fall]',
        'seasonS': 'str, one of [winter, spring, summer, fall]',
        'atype': 'str, one of [diff, mono, wave, ions]',
        'jtype': 'str, one of [energy, number]'
    }

    if not seasonN:
        missing_params.append('seasonN')
    if not seasonS:
        missing_params.append('seasonS')
    if not atype:
        missing_params.append('atype')
    if not jtype:
        missing_params.append('jtype')

    if len(missing_params) > 0:
        error_message = 'Missing required parameters: '
        error_message += ', '.join(missing_params)
        error_formats = [f"{param} - {param_formats[param]}" for param in missing_params]
        error_message += '; '
        error_message += ''.join(error_formats)
        return jsonify({'error': error_message}), 400

    # Проверка условий для параметров seasonN и seasonS
    valid_seasons = ['winter', 'spring', 'summer', 'fall']
    if seasonN not in valid_seasons:
        return jsonify(
            {'error': f'Invalid value for seasonN parameter. Allowed values: {", ".join(valid_seasons)}'}), 400
    if seasonS not in valid_seasons:
        return jsonify(
            {'error': f'Invalid value for seasonS parameter. Allowed values: {", ".join(valid_seasons)}'}), 400

    # Проверка условия для параметра atype
    valid_atypes = ['diff', 'mono', 'wave', 'ions']
    if atype not in valid_atypes:
        return jsonify({'error': f'Invalid value for atype parameter. Allowed values: {", ".join(valid_atypes)}'}), 400

    # Проверка условия для параметра jtype
    valid_jtypes = ['energy', 'number']
    if jtype not in valid_jtypes:
        return jsonify({'error': f'Invalid value for jtype parameter. Allowed values: {", ".join(valid_jtypes)}'}), 400

    fig1, fig2 = draw_seasonal_flux(seasonN, seasonS, atype, jtype)
    combined_image = io.BytesIO()

    fig1.savefig(combined_image, format='png')
    fig2.savefig(combined_image, format='png')
    # Переход на начало файла
    combined_image.seek(0)
    # Закрытие рисунков
    plt.close(fig1)
    plt.close(fig2)
    # Возврат объединенной картинки в качестве файла
    return send_file(combined_image, mimetype='image/png')


@app.route('/api/v1/draw_conductance', methods=['GET'])
def conductance():
    dt = request.args.get('dt')
    hemi = request.args.get('hemi')
    # Проверка обязательности всех параметров
    missing_params = []
    param_formats = {
        'dt': 'yyyy-mm-ddThh:mm:ss',
        'hemi': 'N or S'
    }

    if not dt:
        missing_params.append('dt')
    if not hemi:
        missing_params.append('hemi')

    if len(missing_params) > 0:
        error_message = 'Missing required parameters: '
        error_message += ', '.join(missing_params)
        error_formats = [f"{param} - {param_formats[param]}" for param in missing_params]
        error_message += '; '
        error_message += ''.join(error_formats)
        return jsonify({'error': error_message}), 400

    try:
        parsed_dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        hour = parsed_dt.hour
        minutes = parsed_dt.minute
        seconds = parsed_dt.second
        dt = datetime(parsed_dt.year, parsed_dt.month, parsed_dt.day, hour, minutes, seconds)
    except ValueError:
        return jsonify({'error': f'Invalid format for dt parameter. Expected format: 2023-03-02T10:00:00'}), 400

    valid_hemi = ['N', 'S']

    if hemi not in valid_hemi:
        return jsonify(
            {'error': f'Invalid value for seasonN parameter. Allowed values: {", ".join(valid_hemi)}'}), 400

    f = draw_conductance(dt, hemi)
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close(f)
    return send_file(image_stream, mimetype='image/png')


@app.route('/api/v1/solar_wind_data', methods=['GET'])
def solar_wind_data():
    dt = request.args.get('dt')
    missing_params = []
    param_formats = {
        'dt': 'yyyy-mm-ddThh:mm:ss',
    }
    if not dt:
        missing_params.append('dt')

    if len(missing_params) > 0:
        error_message = 'Missing required parameters: '
        error_message += ', '.join(missing_params)
        error_formats = [f"{param} - {param_formats[param]}" for param in missing_params]
        error_message += "; "
        error_message += "; ".join(error_formats)
        return jsonify({'error': error_message}), 400

    try:
        parsed_dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        hour = parsed_dt.hour
        minutes = parsed_dt.minute
        seconds = parsed_dt.second
        dt = datetime(parsed_dt.year, parsed_dt.month, parsed_dt.day, hour, minutes, seconds)
    except ValueError:
        return jsonify({'error': f'Invalid format for dt parameter. Expected format: 2023-03-02T10:00:00'}), 400

    jd = special_datetime.datetime2jd(dt)

    f = plt.figure(figsize=(8, 11))
    sw = ovation_utilities.read_solarwind(dt)
    sw4avg = ovation_utilities.hourly_solarwind_for_average(dt)
    avgsw = ovation_utilities.calc_avg_solarwind(dt)

    n_plots = len(avgsw.keys())
    axs = [f.add_subplot(n_plots, 1, i) for i in range(1, n_plots + 1)]
    for i, swvar in enumerate(avgsw):
        axs[i].plot(sw['jd'], sw[swvar], 'k-', label=swvar)
        axs[i].plot(sw4avg['jd'], sw4avg[swvar], 'b.', label='hour average')
        axs[i].plot(jd, avgsw[swvar], 'go', label='5 hour weighted average')
        axs[i].set_ylabel(swvar)
        axs[i].legend()

    f.suptitle(str(dt))
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close(f)
    return send_file(image_stream, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=False)
