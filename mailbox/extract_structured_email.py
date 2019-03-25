# from bs4 import BeautifulSoup
# import re
# from bean import mail_bean
# import methods
# from slack import slack_integration
# import schedule
# import time
# from mailbox import connect_to_email_server
#
# account = connect_to_email_server.connect_to_server()
#
# def extract__structured_email():
#
#     for item in account.inbox.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM'):
#
#         """ Extract email contents """
#
#         subject_email = item.subject
#         from_email = item.sender.email_address
#         date_email = item.datetime_received
#
#         soup = BeautifulSoup(item.body, 'html.parser')
#         body_text = soup.get_text()
#         body_text = re.sub("<!-- p { margin-top: 0px; m", " ", body_text)
#         body_text = re.sub("argin-bottom: 0px; }-->", " ", body_text)
#         body = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())
#
#         """" Create Instance of mail bean """
#
#         mail = mail_bean.MailBean(subject_email, from_email, date_email, body)
#
#         """ Check for existing incident """
#
#         correlate_result, correlate_result_status, correlate_link = methods.correlate_incident(mail)
#
#         if (correlate_result_status):
#
#             """ If existing ticket is available, post the subject of new email and time of occurence in the WORK NOTES of existing ticket """
#
#             work_notes = "New alert: \n\n" + "Short Description: " + subject_email + "\n\n" + "Time of Occurence: " + str(
#                 date_email)
#
#             methods.update_worknotes(correlate_result, work_notes)
#
#             """ Respond to the reporter with existing ticket details"""
#
#             correlation_reply_mail = "Hi, \n\n" + "Your request has already being worked on " + correlate_result + ' :\n ' + correlate_link
#             item.reply_all(subject = correlate_result + " : " + subject_email, body = correlation_reply_mail)
#             item.is_read = True
#
#             """ Move email to Actioned Alarms folder"""
#
#             item.move(to_folder=account.inbox / '3. NOC Follow Ups/Updates' / '3. Ignoreable Alarms' / 'Ignored Alarms' / '2. Actioned Alarms (GREY)')
#
#         else:
#
#             """ Create New Incident"""
#
#             new_incident = methods.create_incident(mail)
#             new_incident_url = "https://dev34906.service-now.com/nav_to.do?uri=incident.do?sys_id=" + new_incident['sys_id']
#
#             """Posting new ticket details in slack"""
#
#             message_slack = '<' + new_incident_url + '|' + new_incident['number'] + '> ' + new_incident['short_description'] + ' ' + new_incident['severity'] + "-Low"
#             channel = '#edwinsamples'
#             slack_integration.post_in_slack(message_slack, channel)
#
#             """ Respond to the reporter with new ticket details"""
#
#             message_reply_email = "Hi, \n\n" + "Please find the ticket created for your request" + "\n\n" + new_incident['number'] + '  :  ' + new_incident['short_description'] + '     ' + new_incident['severity'] + "-Low" + "\n" + new_incident_url
#             item.reply_all(subject=new_incident['number'] + " : " + subject_email, body=message_reply_email)
#             item.is_read = True
#
#             """ Move email to Actioned Alarms folder"""
#
#             item.move(to_folder=account.inbox / '3. NOC Follow Ups/Updates' / '3. Ignoreable Alarms' / 'Ignored Alarms' / '2. Actioned Alarms (GREY)')
#
# """ Scheduling """
#
# if __name__ == '__main__':
#     extract__structured_email()
#
# schedule.every(5).seconds.do(extract__structured_email())
#
# while True:
#     """
#     This While loop should be there for scheduler to run!!!!
#     """
#     schedule.run_pending()
#     time.sleep(1)