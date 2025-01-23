import pika
import time
import json

rabbit_credentials = pika.PlainCredentials(username="guest", password="guest")

def wait_for_rabbitmq():
    max_retries = 10
    retry_interval = 5
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="localhost", credentials=rabbit_credentials
                )
            )
            print("Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(
                f"RabbitMQ not ready, retrying in {retry_interval} seconds... (Attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(retry_interval)
    print("RabbitMQ service is still unavailable after max retries. Exiting.")
    raise Exception("Could not connect to RabbitMQ after multiple retries.")

connection = wait_for_rabbitmq()
channel = connection.channel()
channel.exchange_declare(exchange="events", exchange_type="topic")

channel.queue_declare(queue="test_queue", exclusive=True)
channel.queue_bind(
    exchange="events", queue="test_queue", routing_key="booking.change"
)

def change_booking(ch, method, properties, body):
    entry = json.loads(body.decode())
    print(f"Received {entry}")

channel.basic_consume(
    queue="test_queue", on_message_callback=change_booking, auto_ack=True
)
channel.start_consuming()