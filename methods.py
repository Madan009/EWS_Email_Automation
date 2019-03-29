import requests
import re
user = 'admin'
pwd = 'India@123'

headers = {"Content-Type": "application/json", "Accept": "application/json"}

def correlate_incident(mail):

    #Setting the Co related Incs and the availability as false
    correlated_inc =''
    incident_available =False

    #setting the short description as mail subject
    short_description = mail.subject_email

    # url = 'https://dev34906.service-now.com/api/now/table/incident?sysparm_query=active%3Dtrue%5Eshort_descriptionLIKE'+short_description+'%5Eincident_stateIN1%2C2%2C3&sysparm_display_value=false&sysparm_exclude_reference_link=true&sysparm_fields=number%2Cwork_notes_list%2Cincident_state%2Cshort_description&sysparm_limit=10'
    url = 'https://dev34906.service-now.com/api/now/table/incident?sysparm_query=active%3Dtrue%5Eshort_descriptionLIKE'+short_description+'%5Eincident_state%3D2%5EORincident_state%3D1&sysparm_fields=number%2Csys_id&sysparm_limit=10'

    response = requests.get(url, auth=(user, pwd), headers=headers)

    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    data = response.json()

    if(len(data['result'])!=0):
        incident_available = True
        correlated_inc = data['result'][0]['number']
        correlated_url = "https://dev34906.service-now.com/nav_to.do?uri=incident.do?sys_id=" + data['result'][0]['sys_id']
        return correlated_inc, incident_available, correlated_url

    return ('',incident_available,'')

def update_worknotes(incident_number, work_notes):

    # fetch sys_id
    url = 'https://dev34906.service-now.com/api/now/table/incident?sysparm_query=active%3Dtrue%5Enumber%3D'+incident_number+'&sysparm_fields=sys_id&sysparm_limit=1'

    # Do the HTTP request
    response = requests.get(url, auth=(user, pwd), headers=headers)

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    sys_id = data['result'][0]['sys_id']

    # post in work_notes
    url = 'https://dev34906.service-now.com/api/now/table/incident/'+sys_id+''

    worknotes_update_response = requests.patch(url, auth=(user, pwd), headers=headers,
                              json={"work_notes": work_notes})
    # Check for HTTP codes other than 200
    if worknotes_update_response.status_code != 200:
        print('Status:', worknotes_update_response.status_code, 'Headers:', worknotes_update_response.headers, 'Error Response:', worknotes_update_response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data

    data = worknotes_update_response.json()
    return True

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

def update_followUps_worknotes(email_subject, work_notes):
    short_description = email_subject
    incident_number = re.search('(\w+)$', short_description).group()

    url = 'https://dev34906.service-now.com/api/now/table/incident?sysparm_query=active%3Dtrue%5Enumber%3D'+incident_number+'&sysparm_fields=sys_id&sysparm_limit=1'

    # Do the HTTP request
    response = requests.get(url, auth=(user, pwd), headers=headers)

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    sys_id = data['result'][0]['sys_id']

    # post in work_notes
    url = 'https://dev34906.service-now.com/api/now/table/incident/'+sys_id +''


    worknotes_update_response = requests.patch(url, auth=(user, pwd), headers=headers,
                                               json={"work_notes": work_notes})
    # Check for HTTP codes other than 200
    if worknotes_update_response.status_code != 200:
        print('Status:', worknotes_update_response.status_code, 'Headers:', worknotes_update_response.headers,
              'Error Response:', worknotes_update_response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data

    data = worknotes_update_response.json()


def resolve_ticket(email_subject):
    subject_email = email_subject
    short_description = subject_email.replace("OK:", "ALARM:")

    url = 'https://dev34906.service-now.com/api/now/table/incident?sysparm_query=active%3Dtrue%5Eshort_descriptionLIKE'+short_description+'%5Eincident_state%3D2%5EORincident_state%3D1&sysparm_fields=number%2Csys_id&sysparm_limit=10'

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    response = requests.get(url, auth=(user, pwd), headers=headers)

    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    data = response.json()

    if (len(data['result']) != 0):
        resolve_inc = data['result'][0]['number']
        resolve_sysID = data['result'][0]['sys_id']

        close_code = "Solved (Permanently)"
        resolved_by = "Maharaja P"
        close_notes = "Alert turned to OK status "
        state = "Resolved"
        work_notes = subject_email + "\n\n" + "Since we got OK status, the ticket has been resolved"
        url = 'https://dev34906.service-now.com/api/now/table/incident/'+resolve_sysID+'?sysparm_fields=close_code%2Cclosed_by%2Cclose_notes%2Cstate'

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Do the HTTP request
        response = requests.patch(url, auth=(user, pwd), headers=headers, json={"close_code": close_code, "resolved_by": resolved_by, "close_notes": close_notes, "incident_state": state, "work_notes": work_notes})

        # Check for HTTP codes other than 200
        if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
            exit()

        # Decode the JSON response into a dictionary and use the data
        data = response.json()
        return resolve_inc
