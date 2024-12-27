import pika
import time
import json

rabbit_credentials = pika.PlainCredentials(username="guest", password="guest")

def publish_new_apartments(id:str):
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange='events', exchange_type='topic')
    channel.basic_publish(exchange='events', routing_key='new_apartment', body=json.dumps({"apartment":id}))
    connection.close()

def publish_rem_apartments(id:str):
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange='events', exchange_type='topic')
    channel.basic_publish(exchange='events', routing_key='rem_apartment', body=json.dumps({"apartment":id}))
    connection.close()

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