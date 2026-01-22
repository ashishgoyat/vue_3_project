from celery import shared_task

@shared_task(ignore_results = False, name = "download_csv_report")
def csv_report():
    return "CSV Report Downloaded Successfully"

@shared_task(ignore_results = False, name = "send_email_notification")
def send_email_notification(email, subject, body):
    return "Email Sent"