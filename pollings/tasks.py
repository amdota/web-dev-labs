import smtplib
import time

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from datetime import datetime

from pollings.models import Question

logger = get_task_logger(__name__)


@shared_task
def send_email(usernames):
    logger.info("Task started")
    sender = 'from@uapolling.com'
    smtp_obj = smtplib.SMTP('localhost', 1025)
    logger.info(usernames)
    for username in usernames:
        logger.info(username)
        user = User.objects.get(username=username)
        message = \
            f"""From: From admins <from@uapolling.com>
To: To {user.username} <{user.email}>
Subject: SMTP e-mail test

Thank you!
        """
        smtp_obj.sendmail(sender, [user.email], message)
    async_to_sync(get_channel_layer().group_send)(
        "admin_group",
        {
            "type": "completed_task",
            "completedTask": {
                "name": "email sending",
                "data": usernames,
                "result": "successful sending",
                "endDate": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        }
    )


@shared_task()
def calculate_all_votes():
    total_votes = 0
    for question in Question.objects.all():
        for answer in question.answers.all():
            total_votes += answer.voters.count()
    # simulating long task
    time.sleep(3)
    async_to_sync(get_channel_layer().group_send)(
        "admin_group",
        {
            "type": "completed_task",
            "completedTask": {
                "name": "allVotesCalculating",
                "data": "no data",
                "result": total_votes,
                "endDate": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        }
    )


@shared_task()
def generate_report():
    report_file_name = f"report-{datetime.now().strftime('%d-%m-%Y')}"
    with open(report_file_name, 'w') as f:
        f.write(f"Today app has {Question.objects.count()} questions\n")
        f.write(f"We have {User.objects.count()} users\n")
        f.write(f"And something else...")
    # simulating long task
    time.sleep(3)
    async_to_sync(get_channel_layer().group_send)(
        "admin_group",
        {
            "type": "completed_task",
            "completedTask": {
                "name": "report generating",
                "data": "no data",
                "result": f"{report_file_name} was generated",
                "endDate": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        }
    )
