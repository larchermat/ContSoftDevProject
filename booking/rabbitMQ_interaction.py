import pika
import pika.channel
import pika.exceptions
import db_interaction as dbi
import time
import json

rabbit_credentials = pika.PlainCredentials(username="guest", password="guest")

def start_consumer():
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange="events", exchange_type="topic")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name_new = result.method.queue
    channel.queue_bind(
        exchange="events", queue=queue_name_new, routing_key="apartment.new"
    )

    def new_apartment(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.add_apartment(entry["id"])

    channel.basic_consume(
        queue=queue_name_new, on_message_callback=new_apartment, auto_ack=True
    )

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name_rem = result.method.queue
    channel.queue_bind(
        exchange="events", queue=queue_name_rem, routing_key="apartment.remove"
    )

    def remove_apartment(ch, method, properties, body):
        entry = json.loads(body.decode())
        to_delete = dbi.get_bookings_per_apartment(entry["id"])
        dbi.remove_apartment(entry["id"])
        for booking in to_delete:
            publish_event("events", "booking.remove", {"id": booking["id"]})

    channel.basic_consume(
        queue=queue_name_rem, on_message_callback=remove_apartment, auto_ack=True
    )

    try:
        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker as e:
        print("Broker closed connection")
    finally:
        exit()


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


def publish_event(exchange: str, routing_key: str, event: dict):
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type="topic")
    channel.basic_publish(
        exchange=exchange, routing_key=routing_key, body=json.dumps(event)
    )
    connection.close()
