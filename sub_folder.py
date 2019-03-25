# from exchangelib import Account, DELEGATE, Configuration, ServiceAccount
# from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
# import urllib3
# from bs4 import BeautifulSoup
# from slack import slack_integration
# import re
# from bean import mail_bean
# import methods
#
# urllib3.disable_warnings()
#
# BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
#
# credentials = ServiceAccount(username='1051058@tcsmfdm.com', password='India@2030')
# config = Configuration(server='win9595.tcsmfdm.com', credentials=credentials)
# account = Account(primary_smtp_address="1051058@tcsmfdm.com",
#                   config=config,
#                   autodiscover=False,
#                   access_type=DELEGATE)
#
# def extract_email():
#     Pending_Alarms = account.inbox / 'Pending Alarms'
#     for item in Pending_Alarms.filter(is_read=False, subject__istartswith='[EXTERNAL] ALARM'):
#     # for item in account.inbox.filter(is_read=False, subject__istartswith = '[EXTERNAL] ALARM'):
#
#         subject_email = item.subject
#         print(subject_email)
#         from_email = item.sender.email_address
#         date_email = item.datetime_received
#
#         soup = BeautifulSoup(item.body, 'html.parser')
#         body_text = (soup.get_text())
#         body_text = re.sub("<!-- p { margin-top: 0px; m", " ", body_text)
#         body_text = re.sub("argin-bottom: 0px; }-->", " ", body_text)
#         body = re.sub(r'(\n\s*)+\n+', '\n\n', body_text.strip())
#
#         mail = mail_bean.MailBean(subject_email, from_email, date_email, body)
#
#         # Check for existing incident
#         correlate_result, correlate_result_status, correlate_link = methods.correlate_incident(mail)
#         # If there are any co related incidents available then post update the worknotes of the Incident with the new mail
#         if (correlate_result_status):
#
#             # Generating the work notes to be updated
#             work_notes = "New alert: \n\n" + "Short Description: " + subject_email + "\n\n" + "Time of Occurence: " + str(date_email)
#             print(work_notes)
#
#             # Updating the work notes of the Incident
#             methods.update_worknotes(correlate_result, work_notes)
#
#             correlation_reply_mail = "Hi, \n\n" + "We already have " + correlate_result + ' : ' + correlate_link + "created and being worked on for your request"
#             item.move(to_folder=account.inbox / 'Correlated Alarms')
#             item.reply_all(subject=correlate_result + " : " + subject_email, body=correlation_reply_mail)
#             item.is_read = True
#
#         # Create a new Incident for the mail
#         else:
#             # Create Incident
#             new_incident = methods.create_incident(mail)
#             new_incident_url = "https://dev34906.service-now.com/nav_to.do?uri=incident.do?sys_id=" + new_incident['sys_id']
#
#             message = '<' + new_incident_url + '|' + new_incident['number'] + '> ' + new_incident[
#                 'short_description'] + ' ' + new_incident['severity'] + "-Low"
#
#             message_reply_email = "Hi, \n\n" + "Please find the ticket created for your request" + "\n\n" + new_incident[
#                 'number'] + '  :  ' + new_incident['short_description'] + '     ' + new_incident[
#                                       'severity'] + "-Low" + "\n" + new_incident_url
#             print(message_reply_email)
#
#             channel = '#edwinsamples'
#             slack_integration.post_in_slack(message, channel)
#             item.move(to_folder=account.inbox / 'Actioned Alarms')
#             item.reply_all(subject=new_incident['number'] + " : " +subject_email, body=message_reply_email)
#             item.is_read = True
#         extract_email()
# # if __name__ == '__main__':
# #     extract_email()
# #
# # schedule.every(5).seconds.do(extract_email)
# #
# # while True:
# #     """
# #     This While loop should be there for scheduler to run!!!!
# #     """
# #     schedule.run_pending()
# #     time.sleep(1)
#
#
#
#
#
#
