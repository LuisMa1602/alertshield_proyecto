
from flask import Flask, request, jsonify
import redis
import json
import logging

app = Flask(__name__)

# Configuración de logging local
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar conexión a Redis con manejo de error
try:
    r = redis.Redis(host='redis', port=6379, socket_connect_timeout=5)
    r.ping()  # Verifica conexión inicial
    logger.info("Conexión a Redis establecida.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Fallo en la conexión a Redis: {e}")
    r = None  # Marcar como no disponible

@app.route('/log', methods=['POST'])
def log():
    if not r:
        return jsonify({'status': 'error', 'message': 'Redis no disponible'}), 503

    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Contenido no es JSON válido'}), 400

    try:
        data = request.get_json()
        r.publish('logs', json.dumps(data))
        logger.info(f"Log recibido y publicado: {data}")
        return jsonify({'status': 'log recibido'}), 200
    except Exception as e:
        logger.error(f"Error procesando log: {e}")
        return jsonify({'status': 'error', 'message': 'Fallo interno'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
