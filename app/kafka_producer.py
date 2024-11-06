from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import random
from config.config import Config
import logging

class IoTProducer:
    def __init__(self):
        self._connect_with_retry()

    def _connect_with_retry(self, max_retries=5, retry_delay=5):
        for i in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                print("Successfully connected to Kafka")
                return
            except NoBrokersAvailable:
                if i < max_retries - 1:
                    print(f"Kafka not available, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception("Failed to connect to Kafka after multiple retries")

    def simulate_sensor_data(self):
        while True:
            sensor_data = {
                'sensor_id': random.randint(1, 5),
                'temperature': round(random.uniform(20, 30), 2),
                'humidity': round(random.uniform(30, 70), 2),
                'light': round(random.uniform(0, 1000), 2),
                'timestamp': time.time()
            }
            
            self.producer.send(Config.KAFKA_TOPIC, sensor_data)
            print(f"Sent: {sensor_data}")
            time.sleep(2)

if __name__ == '__main__':
    producer = IoTProducer()
    producer.simulate_sensor_data() 