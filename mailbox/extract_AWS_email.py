from bs4 import BeautifulSoup
import re
from bean import mail_bean
import methods
from slack import slack_integration
from mailbox import connect_to_email_server

account = connect_to_email_server.connect_to_server()

def extract_new_structured_email():
    # schedule.every(5).seconds.do(extract_new_structured_email)
    for new_structured_email in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM:'):

        subject_email = new_structured_email.subject
        from_email = new_structured_email.sender.email_address
        date_email = new_structured_email.datetime_received
        # to_email = new_structured_email.to_recipients
        # cc_email = new_structured_email.cc_recipients

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
            # "To :" + to_email + "CC :" + cc_email +
            # Updating the work notes of the Incident
            methods.update_worknotes(correlate_result, work_notes)

            correlation_reply_mail = "Hi, \n\n" + "Your request is already being worked under \n " + correlate_result + ' :\n ' + correlate_link

            new_structured_email.reply_all(subject= "Re : " + subject_email + " " +correlate_result, body=correlation_reply_mail)
            new_structured_email.is_read = True

            new_structured_email.move(
                to_folder=account.inbox / '3. NOC Follow Ups' / '3. Ignoreable Alarms' / 'Ignored Alarms' / 'New Issues (Actioned)' / '2. Actioned Alarms (GREY)')
        # Create a new Incident for the mail
        else:
            # Create Incident
            new_incident = methods.create_incident(mail)
            new_incident_url = "https://dev34906.service-now.com/nav_to.do?uri=incident.do?sys_id=" + new_incident['sys_id']

            message_slack = '<' + new_incident_url + '|' + new_incident['number'] + '> ' + new_incident[
                'short_description'] + ' ' + new_incident['severity'] + "-Low"

            message_reply_email = "Hi, \n\n" + "Please find the ticket created for your request" + "\n\n" + new_incident[
                'number'] + '  :  ' + new_incident['short_description'] + '     ' + new_incident[
                                      'severity'] + "-Low" + "\n" + new_incident_url

            channel = '#edwinsamples'
            slack_integration.post_in_slack(message_slack, channel)

            new_structured_email.move(to_folder=account.inbox / '3. NOC Follow Ups' / '3. Ignoreable Alarms' / 'Ignored Alarms' / 'New Issues (Actioned)' / '2. Actioned Alarms (GREY)')

            new_structured_email.reply_all(subject="Re : " +subject_email + " " +new_incident['number'], body=message_reply_email)
            new_structured_email.is_read = True
