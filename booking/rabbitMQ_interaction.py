import pika
import db_interaction as dbi
import time
import json

rabbit_credentials = pika.PlainCredentials(username="guest", password="guest")

def start_consumer():
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange='events', exchange_type='topic')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name_new = result.method.queue
    channel.queue_bind(exchange='events', queue=queue_name_new, routing_key='new_apartment')

    def new_apartment(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.add_apartment(entry["apartment"])

    channel.basic_consume(queue=queue_name_new, on_message_callback=new_apartment, auto_ack=True)

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name_rem = result.method.queue
    channel.queue_bind(exchange='events', queue=queue_name_rem, routing_key='rem_apartment')

    def remove_apartment(ch, method, properties, body):
        entry = json.loads(body.decode())
        dbi.remove_apartment(entry["apartment"])

    channel.basic_consume(queue=queue_name_rem, on_message_callback=remove_apartment, auto_ack=True)
    
    channel.start_consuming()

def wait_for_rabbitmq():
    max_retries = 10
    retry_interval = 5
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', credentials=rabbit_credentials)
            )
            print("Connected to RabbitMQ!")
            return  connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ not ready, retrying in {retry_interval} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_interval)
    print("RabbitMQ service is still unavailable after max retries. Exiting.")
    raise Exception("Could not connect to RabbitMQ after multiple retries.")