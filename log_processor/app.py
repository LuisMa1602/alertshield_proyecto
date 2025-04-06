import redis
import json
import time
import requests
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = 'redis'
REDIS_PORT = 6379
BOT_URL = 'http://notif_bot:8000/alert'

# Intentar conexión a Redis
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=5)
    r.ping()
    logger.info("Conexión a Redis establecida.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"No se pudo conectar a Redis: {e}")
    exit(1)

# Suscripción al canal
p = r.pubsub()
p.subscribe('logs')
logger.info("Suscrito al canal 'logs'.")

def enviar_alerta(alert):
    for intento in range(3):  # Reintentos con backoff exponencial
        try:
            response = requests.post(BOT_URL, json=alert, timeout=5)
            response.raise_for_status()
            logger.info(f"Alerta enviada: {alert}")
            return
        except requests.exceptions.RequestException as e:
            wait = 2 ** intento
            logger.warning(f"Fallo al enviar alerta, reintento en {wait}s. Error: {e}")
            time.sleep(wait)
    logger.error("No se pudo enviar la alerta después de varios intentos.")

# Loop principal
for message in p.listen():
    if message['type'] != 'message':
        continue

    try:
        log = json.loads(message['data'])
        logger.info(f"Procesando log: {log}")

        msg = log.get('message', '')
        if 'error' in msg.lower():
            alert = {
                'message': msg,
                'service': log.get('service', 'desconocido')
            }
            enviar_alerta(alert)

    except json.JSONDecodeError:
        logger.warning("Mensaje no es JSON válido, se ignora.")
    except Exception as e:
        logger.exception(f"Error inesperado procesando el mensaje: {e}")
