""" Packages needed"""

from exchangelib import Account, DELEGATE, Configuration, ServiceAccount
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3
from bs4 import BeautifulSoup
import schedule
import re
from bean import mail_bean
from Controller import iop_automation_methods, slack_integration

urllib3.disable_warnings()

BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

""" Connect to server and login to Mailbox"""

credentials = ServiceAccount(username='1051058@tcsmfdm.com', password='India@2030')
config = Configuration(server='win9595.tcsmfdm.com', credentials=credentials)
account = Account(primary_smtp_address="1051058@tcsmfdm.com",
                  config=config,
                  autodiscover=False,
                  access_type=DELEGATE)

def extract_new_structured_email():

    """ Fetch email content of New Email Triggered """

    for new_structured_email in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM:'):

        """ Fetch email header """

        subject_email = new_structured_email.subject
        from_email = new_structured_email.sender.email_address
        date_email = new_structured_email.datetime_received

        """ Fetch email body """

        soup = BeautifulSoup(new_structured_email.body, 'html.parser')
        body_text = (soup.get_text())
        body_text = re.sub("<!-- p { margin-top: 0px; m", " ", body_text)
        body_text = re.sub("argin-bottom: 0px; }-->", " ", body_text)
        body = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())

        mail = mail_bean.MailBean(subject_email, from_email, date_email, body)

        """ New email received is checked for existing ticket, if found, alert is correlared. If not a new ticket is created """

        correlate_result, correlate_result_status, correlate_link = iop_automation_methods.correlate_incident(mail)

        if (correlate_result_status):

            """Correlate new email to existing ticket"""

            """post correlated alert details in Slack Channel"""

            message_slack = subject_email + '\n *Correlated to* : ' + correlate_result
            channel = '#edwinsamples'
            slack_integration.post_in_dper_slack(message_slack, channel)

            """ Update Existing ticket worknotes with new alert details"""

            work_notes = "New alert: \n\n" + "From: " + from_email + "Short Description: " + subject_email + "\n\n" + "Time of Occurence: " + str(date_email)
            iop_automation_methods.update_correlated_alert_worknotes(correlate_result, work_notes)

            """Move Correlated email to Actioned Alarms folder in mailbox"""

            new_structured_email.move(
                to_folder=account.inbox / '3. NOC Follow Ups' / '3. Ignoreable Alarms' / 'Ignored Alarms' / 'New Issues (Actioned)' / '2. Actioned Alarms (GREY)')

            """ Reply back to Reporter with correlated alert details"""

            correlation_reply_mail = "Hi, \n\n" + "Your request is already being worked under \n" + correlate_result + ' : ' + correlate_link
            new_structured_email.reply_all(subject="Re : " + subject_email + " " +correlate_result, body=correlation_reply_mail)

            new_structured_email.is_read = False

        else:

            """ Create Ticket"""

            new_incident = iop_automation_methods.create_incident(mail)
            new_incident_url = "https://dev34906.service-now.com/nav_to.do?uri=incident.do?sys_id=" + new_incident['sys_id']
            incident_number = new_incident['number']

            """post new alert details in Slack Channels"""

            message_slack = '<' + new_incident_url + '|' + incident_number + '> ' + new_incident['short_description'] + ' ' + new_incident['severity'] + "-Low"
            channel = '#edwinsamples'
            slack_integration.post_in_dper_slack(message_slack, channel)

            """Move New email to Actioned Alarms folder in mailbox"""

            new_structured_email.move(to_folder=account.inbox / '3. NOC Follow Ups' / '3. Ignoreable Alarms' / 'Ignored Alarms' / 'New Issues (Actioned)' / '2. Actioned Alarms (GREY)')

            """ Reply back to Reporter with new alert details"""

            message_reply_email = "Hi, \n\n" + "Please find the ticket created for your request" + "\n\n" + new_incident['number'] + '  :  ' + new_incident['short_description'] + '     ' + new_incident['severity'] + "-Low" + "\n" + new_incident_url
            new_structured_email.reply_all(subject="Re : " + subject_email + " " +new_incident['number'], body=message_reply_email)

            new_structured_email.is_read = False

""" Any email conversation associated should be updated in ticket """

def follow_up():

    """ Fetch email content of Response Emails Triggered """

    for follow_up_email in account.inbox.filter(is_read=False, subject__icontains='INC'):

        """ Fetch email header """

        subject_email = follow_up_email.subject
        from_email = follow_up_email.sender.email_address
        date_email = follow_up_email.datetime_received

        """ Fetch email body """

        soup = BeautifulSoup(follow_up_email.body, 'html.parser')
        body_text = (soup.get_text())
        body_email = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())
        keyword = 'From:'
        body, body_keyword, body_after_keyword = body_email.partition(keyword)

        """ Update email conversations in the ticket"""

        work_notes = "From : " + from_email + "\n" "Subject : " + subject_email + "\n" + "Time of Occurrence : " + str(date_email) + "\n\n" + body
        iop_automation_methods.update_followUps_worknotes(subject_email, work_notes)

        """Move email to NOC Follow Ups folder in mailbox"""

        follow_up_email.move(to_folder=account.inbox / '3. NOC Follow Ups')

def resolve_aws_incident():

    for aws_email in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] OK:'):

        """ Fetch email content of Response Email Triggered """

        subject_email = aws_email.subject
        resolve_ticket = iop_automation_methods.resolve_ticket(subject_email)

        """Move email to NOC Follow Ups folder in mailbox"""

        aws_email.move(to_folder=account.inbox / '3. NOC Follow Ups')

        """ Reply back to Reporter with ticket closure update"""

        resolve_email_worknotes = "The Ticket has been closed"
        aws_email.reply_all(subject=subject_email + " " + resolve_ticket, body=resolve_email_worknotes)

def outage_predictor():

    """ Fetch count of email triggred for each 5 seconds """

    count = account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM:').count()
    if(count>3):

        """ Notify production support team in slack for more ticket volume"""

        message_slack = "*@prodsupport* There is a spike in AWS alerts triggered \n\n *Alert Count* = " + str(count) + "\n *Time Interval* = 10 seconds \n\n Please refer to *#dper_huddle* slack channel for ticket details\n\n"
        channel = '#prod_support_oncall'
        slack_integration.post_in_tp_slack(message_slack, channel)
    else:
        return None

if __name__ == '__main__':

    """Schedule above methods for every 5 seconds"""

    def schedule_job():

        outage_predictor()
        extract_new_structured_email()
        follow_up()
        resolve_aws_incident()

    schedule.every(10).seconds.do(schedule_job)

    while True:
        """
        This While loop should be there for scheduler to run!!!!
        """
        schedule.run_pending()





