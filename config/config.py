import os

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = 'iot_sensors'
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', True) 