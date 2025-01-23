import pika
import time
import json

rabbit_credentials = pika.PlainCredentials(username="guest", password="guest")


def publish_event(exchange: str, routing_key: str, event: dict):
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type="topic")
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )
    connection.close()


def wait_for_rabbitmq():
    max_retries = 10
    retry_interval = 5
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq", credentials=rabbit_credentials
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
