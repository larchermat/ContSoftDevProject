import pika
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
    queue_name = result.method.queue
    channel.queue_bind(exchange="events", queue=queue_name, routing_key="apartment.new")

    def new_apartment(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.add_apartment(
            entry["id"],
            entry["name"],
            entry["address"],
            entry["noiselevel"],
            entry["floor"],
        )

    channel.basic_consume(
        queue=queue_name, on_message_callback=new_apartment, auto_ack=True
    )

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange="events", queue=queue_name, routing_key="apartment.remove"
    )

    def remove_apartment(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.remove_apartment(entry["apartment"])

    channel.basic_consume(
        queue=queue_name, on_message_callback=remove_apartment, auto_ack=True
    )

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="events", queue=queue_name, routing_key="booking.new")

    def new_booking(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.add_booking(entry["id"], entry["apartment"], entry["start"], entry["end"])

    channel.basic_consume(
        queue=queue_name, on_message_callback=new_booking, auto_ack=True
    )

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange="events", queue=queue_name, routing_key="booking.remove"
    )

    def remove_booking(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.remove_booking(entry["id"])

    channel.basic_consume(
        queue=queue_name, on_message_callback=remove_booking, auto_ack=True
    )

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange="events", queue=queue_name, routing_key="booking.change"
    )

    def change_booking(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.change_booking(entry["id"], entry["start"], entry["end"])

    channel.basic_consume(
        queue=queue_name, on_message_callback=change_booking, auto_ack=True
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
