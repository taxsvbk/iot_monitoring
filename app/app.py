from flask import Flask, render_template, jsonify
from app.kafka_consumer import IoTConsumer
from config.config import Config
import threading

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Kafka consumer
consumer = IoTConsumer()

# Start consuming messages in a separate thread
def start_consuming():
    for message in consumer.consume_messages():
        pass

consumer_thread = threading.Thread(target=start_consuming)
consumer_thread.daemon = True
consumer_thread.start()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/sensor-data')
def get_sensor_data():
    return jsonify(consumer.get_latest_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)