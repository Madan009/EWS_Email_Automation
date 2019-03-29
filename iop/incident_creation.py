import requests

def create_incident(mail):
    short_description = mail.subject_email
    description = (mail.subject_email + mail.from_email + str(mail.date_email) + mail.body)

    url = 'https://dev34906.service-now.com/api/now/table/incident'

    response = requests.post(url, auth=(user, pwd), headers=headers, json={"caller_id": "Maharaja P", "contact_type": "Email", "business_service": "Big Data Service", "severity": "4 - Low", "u_choice_1": "Hazcon", "assignment_group": "TPX-SE-dx-L1_Ops:NTL", "assigned_to": "Sambandan Kumaran", "u_incident_manager_group": "TPX-RE-RP-ProdSupport_X1_Platform:NTL", "u_incident_manager": "Mohammed Jameel Ahmed Junagadh", "short_description": short_description, "description": description})

    if response.status_code != 201:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    data = response.json()
    ticket_details = data['result']
    return ticket_details
