from bs4 import BeautifulSoup
import methods
import re
from mailbox import connect_to_email_server

account = connect_to_email_server.connect_to_server()

def follow_up():

    for follow_up_email in account.inbox.filter(is_read=False, subject__istartswith='Re : '):
        subject_email = follow_up_email.subject
        from_email = follow_up_email.sender.email_address
        date_email = follow_up_email.datetime_received
        soup = BeautifulSoup(follow_up_email.body, 'html.parser')
        body_text = (soup.get_text())
        body_email = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())
        keyword = 'From:'
        body, body_keyword, body_after_keyword = body_email.partition(keyword)
        work_notes = "From : " + from_email + "\n" "Subject : " + subject_email + "\n" + "Time of Occurrence : " + str(date_email) + "\n\n" + body
        # + "To : " + to_email + "\n" + "CC : " + cc_email + "\n" +
        methods.update_followUps_worknotes(subject_email, work_notes)
        follow_up_email.move(to_folder=account.inbox / '3. NOC Follow Ups')