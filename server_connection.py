from exchangelib import Account, DELEGATE, Configuration, ServiceAccount
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3
from bs4 import BeautifulSoup
from slack import slack_integration
import schedule
import time
import re
from bean import mail_bean
import methods

urllib3.disable_warnings()

BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

credentials = ServiceAccount(username='1051058@tcsmfdm.com', password='India@2030')
config = Configuration(server='win9595.tcsmfdm.com', credentials=credentials)
account = Account(primary_smtp_address="1051058@tcsmfdm.com",
                  config=config,
                  autodiscover=False,
                  access_type=DELEGATE)

def extract_new_structured_email():

    for new_structured_email in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM:'):

        subject_email = new_structured_email.subject
        from_email = new_structured_email.sender.email_address
        date_email = new_structured_email.datetime_received

        soup = BeautifulSoup(new_structured_email.body, 'html.parser')
        body_text = (soup.get_text())
        body_text = re.sub("<!-- p { margin-top: 0px; m", " ", body_text)
        body_text = re.sub("argin-bottom: 0px; }-->", " ", body_text)
        body = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())

        mail = mail_bean.MailBean(subject_email, from_email, date_email, body)

        # Check for existing incident
        correlate_result, correlate_result_status, correlate_link = methods.correlate_incident(mail)
        # If there are any co related incidents available then post update the worknotes of the Incident with the new mail
        if (correlate_result_status):

            # Generating the work notes to be updated
            work_notes = "New alert: \n\n" + "From: " + from_email + "Short Description: " + subject_email + "\n\n" + "Time of Occurence: " + str(date_email)

            # Updating the work notes of the Incident
            methods.update_worknotes(correlate_result, work_notes)

            correlation_reply_mail = "Hi, \n\n" + "Your request is already being worked under \n " + correlate_result + ' :\n ' + correlate_link

            new_structured_email.move(
                to_folder=account.inbox / '3. NOC Follow Ups' / '3. Ignoreable Alarms' / 'Ignored Alarms' / 'New Issues (Actioned)' / '2. Actioned Alarms (GREY)')

            new_structured_email.reply_all(subject="Re : " + subject_email + " " +correlate_result, body=correlation_reply_mail)
            new_structured_email.is_read = False


        # Create a new Incident for the mail
        else:
            # Create Incident
            new_incident = methods.create_incident(mail)
            new_incident_url = "https://dev34906.service-now.com/nav_to.do?uri=incident.do?sys_id=" + new_incident['sys_id']
            incident_number = new_incident['number']
            message_slack = '<' + new_incident_url + '|' + new_incident['number'] + '> ' + new_incident[
                'short_description'] + ' ' + new_incident['severity'] + "-Low"

            channel = '#edwinsamples'
            slack_integration.post_in_dper_slack(message_slack, channel)
            slack_integration.post_in_tp_slack(message_slack, channel)

            message_reply_email = "Hi, \n\n" + "Please find the ticket created for your request" + "\n\n" + new_incident[
                'number'] + '  :  ' + new_incident['short_description'] + '     ' + new_incident[
                                      'severity'] + "-Low" + "\n" + new_incident_url
            # work_notes = message_reply_email
            # methods.update_worknotes(incident_number, work_notes)
            new_structured_email.move(
                to_folder=account.inbox / '3. NOC Follow Ups' / '3. Ignoreable Alarms' / 'Ignored Alarms' / 'New Issues (Actioned)' / '2. Actioned Alarms (GREY)')
            new_structured_email.reply_all(subject="Re : " + subject_email + " " +new_incident['number'], body=message_reply_email)

            new_structured_email.is_read = False

def follow_up():
    for follow_up_email in account.inbox.filter(is_read=False, subject__icontains='INC'):
        subject_email = follow_up_email.subject
        from_email = follow_up_email.sender.email_address
        date_email = follow_up_email.datetime_received
        soup = BeautifulSoup(follow_up_email.body, 'html.parser')
        body_text = (soup.get_text())
        body_email = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())
        keyword = 'From:'
        body, body_keyword, body_after_keyword = body_email.partition(keyword)
        work_notes = "From : " + from_email + "\n" "Subject : " + subject_email + "\n" + "Time of Occurrence : " + str(date_email) + "\n\n" + body
        methods.update_followUps_worknotes(subject_email, work_notes)
        follow_up_email.move(to_folder=account.inbox / '3. NOC Follow Ups')

def resolve_aws_incident():

    for aws_email in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] OK:'):
        subject_email = aws_email.subject
        resolve_ticket = methods.resolve_ticket(subject_email)
        aws_email.move(to_folder=account.inbox / '3. NOC Follow Ups')
        resolve_email_worknotes = "The Ticket has been closed"
        aws_email.reply_all(subject=subject_email + " " + resolve_ticket, body=resolve_email_worknotes)

def email_count():
    count = account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM:').count()
    print(count)
    if(count>3):
        message_slack = "@prodsupport There is a spike in AWS alerts triggered. We have " + str(count) + " alerts acknowledged. Please look into #dper-huddle channel for ticket details"
        channel = '#prod_support_oncall'
        slack_integration.post_in_tp_slack(message_slack, channel)
    else:
        return None

if __name__ == '__main__':

    def schedule_job():

        email_count()
        extract_new_structured_email()
        follow_up()
        resolve_aws_incident()

    schedule.every(5).seconds.do(schedule_job)

    while True:
        """
        This While loop should be there for scheduler to run!!!!
        """
        schedule.run_pending()





