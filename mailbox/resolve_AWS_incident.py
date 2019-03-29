import methods
from mailbox import connect_to_email_server

account = connect_to_email_server.connect_to_server()

def resolve_aws_incident():
    # schedule.every(5).seconds.do(resolve_aws_incident)
    for aws_email in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] OK:'):
        subject_email = aws_email.subject
        methods.resolve_AWS_incident(subject_email)
        aws_email.move(to_folder=account.inbox / '3. NOC Follow Ups')