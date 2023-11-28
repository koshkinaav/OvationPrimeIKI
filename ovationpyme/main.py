from ovationpyme.visual_test_ovation_prime import draw_weighted_flux, draw_seasonal_flux
import io
from datetime import datetime
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, send_file, Response

app = Flask(__name__)


# http://localhost:5000/api/v1/draw_weighted_flux?dt=2023-11-28T10:00:00&atype=diff&jtype=energy
# http://localhost:5000/api/v1/draw_seasonal_flux?seasonN=winter&seasonS=summer&atype=diff&jtype=energy

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
    # Сохранение рисунков в памяти в формате PNG
    image_stream1 = io.BytesIO()
    fig1.savefig(image_stream1, format='png')
    image_stream1.seek(0)

    image_stream2 = io.BytesIO()
    fig2.savefig(image_stream2, format='png')
    image_stream2.seek(0)

    plt.close(fig1)
    plt.close(fig2)

    # Создание генератора для потоковой передачи рисунков
    def image_generator():
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + image_stream1.read() + b'\r\n\r\n')
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + image_stream2.read() + b'\r\n\r\n')

    # Возвращение обоих рисунков в формате multipart/x-mixed-replace
    return Response(image_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=False)
