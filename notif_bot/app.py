from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/alert', methods=['POST'])
def alert():
    if not request.is_json:
        logger.warning("Solicitud con contenido no JSON.")
        return jsonify({'status': 'error', 'message': 'Formato no JSON'}), 400

    try:
        data = request.get_json()

        service = data.get('service')
        message = data.get('message')

        if not service or not message:
            logger.warning("Faltan campos en la alerta.")
            return jsonify({'status': 'error', 'message': 'Faltan campos obligatorios'}), 400

        logger.warning(f"⚠️ ALERTA: [{service}] - {message}")
        return jsonify({'status': 'alerta recibida'}), 200

    except Exception as e:
        logger.exception("Error al procesar alerta")
        return jsonify({'status': 'error', 'message': 'Error interno'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)