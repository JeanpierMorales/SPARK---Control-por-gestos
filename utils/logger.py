import logging
import datetime

# Configurar el logger
logger = logging.getLogger('SPARK')
logger.setLevel(logging.DEBUG)  # Nivel mínimo de logging

# Crear un handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Crear un formatter para incluir timestamp, nivel y mensaje
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Agregar el handler al logger
logger.addHandler(console_handler)

def log(message, level='info'):
    """
    Función para loggear mensajes con diferentes niveles.
    
    Parámetros:
    - message: El mensaje a loggear
    - level: Nivel de logging ('debug', 'info', 'warning', 'error', 'critical')
    """
    if level.lower() == 'debug':
        logger.debug(message)
    elif level.lower() == 'info':
        logger.info(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'critical':
        logger.critical(message)
    else:
        logger.info(message)  # Por defecto info

# Mantener compatibilidad con la función anterior
def log_old(message):
    """
    Función antigua para compatibilidad. Ahora usa el nuevo logger.
    """
    log(message, 'info')
