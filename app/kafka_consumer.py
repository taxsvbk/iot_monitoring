from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import time
from config.config import Config
from collections import defaultdict

class IoTConsumer:
    def __init__(self):
        self._connect_with_retry()
        self.latest_data = defaultdict(dict)

    def _connect_with_retry(self, max_retries=5, retry_delay=5):
        for i in range(max_retries):
            try:
                self.consumer = KafkaConsumer(
                    Config.KAFKA_TOPIC,
                    bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    auto_offset_reset='latest',
                    enable_auto_commit=True
                )
                print("Successfully connected to Kafka Consumer")
                return
            except NoBrokersAvailable:
                if i < max_retries - 1:
                    print(f"Kafka not available, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception("Failed to connect to Kafka after multiple retries")

    def consume_messages(self):
        for message in self.consumer:
            data = message.value
            sensor_id = data['sensor_id']
            self.latest_data[sensor_id] = data
            yield data

    def get_latest_data(self):
        return list(self.latest_data.values())
