import pika
import json
import os, time

from dotenv import load_dotenv
from image_build_util import handle_message
from logger import logger

# Get environment variables
load_dotenv("./secrets/.env")
AMQP_HOSTNAME = os.getenv("AMQP_HOSTNAME")
AMQP_PORT = 5672
AMQP_USERNAME = os.getenv('AMQP_USERNAME')
AMQP_PASSWORD = os.getenv('AMQP_PASSWORD')
credentials = pika.PlainCredentials(AMQP_USERNAME, AMQP_PASSWORD)

# Create a connection and channel
retry_timer = 2
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=AMQP_HOSTNAME, port=AMQP_PORT,virtual_host='/',credentials=credentials))
        logger.info("Connected to Rabbit MQ SUCCESS!")
        break
    except:
        logger.info(f"Connecting to RabbitMQ Failed... Retrying in {retry_timer} seconds")
        time.sleep(retry_timer)
        retry_timer += 2


channel = connection.channel()
# Queues and exchange's names
TO_SERVICE_QUEUE = 'queue.imageBuilder.toService'
FROM_SERVICE_QUEUE = 'queue.imageBuilder.fromService'
BUILDER_EXCHANGE = 'topic.imageBuilder'

# Routing keys
TO_SERVICE_ROUTING_KEY = 'imageBuilder.toService.*'
FROM_SERVICE_ROUTING_KEY = 'imageBuilder.fromService.imageBuilt'

# Declare queue
channel.queue_declare(
    queue=TO_SERVICE_QUEUE,
    durable=True
)

# Declare exchange
channel.exchange_declare(
    exchange=BUILDER_EXCHANGE,
    exchange_type='topic',
    durable=True
)

# Queue bind
channel.queue_bind(
    exchange=BUILDER_EXCHANGE,
    queue=FROM_SERVICE_QUEUE,
    routing_key=FROM_SERVICE_ROUTING_KEY
)


def custom_callback(ch, method, props, body):
    message_data = json.loads(body.decode('utf-8'))
    
    # If message was not handled successfully
    if not handle_message(message_data):
        status = "FAIL"
        logger.error("Image build FAILED!")
    
    # Acknowledge upon successful
    else:
        status = "SUCCESS"
        logger.info("Image build COMPLETE!")
    
    logger.info("===============================")
        
    # Respond to process engine through fromService queue
    corId = 'corId'
    response_body = f'"corId": "{message_data[corId]}", "buildStatus": "{status}"'
    
    channel.basic_publish(
        exchange=BUILDER_EXCHANGE,
        routing_key=FROM_SERVICE_ROUTING_KEY,
        body='{' + response_body + '}'
    )
    
    # Acknowledege message
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue=TO_SERVICE_QUEUE,
    on_message_callback=custom_callback,
    auto_ack=False
)

logger.info("Waiting for messages... To exit, press CTRL+C")
channel.start_consuming()