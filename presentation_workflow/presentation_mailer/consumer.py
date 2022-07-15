import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()



while True:
    try:
        def process_approval(ch, method, properties, body):
            print("sending approval email")
            content = json.loads(body)
            title = content["title"]
            name = content["presenter_name"]
            recipient = content["presenter_email"]
            sender = "admin@conference.go"
            subject = "Your presentation has been accepted"
            message = f"{name}, we're happy to tell you that your presentation {title} has been accepted"
            send_mail(subject, message, sender, [recipient], fail_silently=False)


        def process_rejection(ch, method, properties, body):
            print("sending rejection email")
            content = json.loads(body)
            title = content["title"]
            name = content["presenter_name"]
            recipient = content["presenter_email"]
            sender = "admin@conference.go"
            subject = "Your presentation has been accepted"
            message = f"{name}, we're sorry to tell you that your presentation {title} has been rejected"
            send_mail(subject, message, sender, [recipient], fail_silently=False)


        print("running main")
        parameters = pika.ConnectionParameters(host='rabbitmq')
        connection = pika.BlockingConnection(parameters)
        channels = connection.channel()
        channels.queue_declare(queue='presentation_approvals')
        channels.basic_consume(
            queue='presentation_approvals',
            on_message_callback=process_approval,
            auto_ack=True,
        )
        channels = connection.channel()
        channels.queue_declare(queue='presentation_rejections')
        channels.basic_consume(
            queue='presentation_rejections',
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        channels.start_consuming()
        # I'm not totally sure what the black magic is provided by RabbitMQ however channels almost
        # acts as a dictionary or list and holds alllllll of the channels that we connect and declare
        # you only need to call start_consuming once and it will watch all of those channels
    
    
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)










# def process_approval(ch, method, properties, body):
    
#     parameters = pika.ConnectionParameters(host='rabbitmq')
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     channel.queue_declare(queue='presentation_approvals')
#     channel.basic_consume(
#         queue='presentation_approvals',
#         # on_message_callback=process_message,
#         auto_ack=True,
#     )
#     print("processed_approval")

#     content = json.loads(body)
#     title = content["title"]
#     name = content["presenter_name"]
#     recipient = content["presenter_email"]
#     sender = "admin@conference.go"
#     subject = "Your presentation has been accepted"
#     message = f"{name}, we're happy to tell you that your presentation {title} has been accepted"
#     send_mail(subject, message, sender, [recipient], fail_silently=False)
#     print("processed_approval")