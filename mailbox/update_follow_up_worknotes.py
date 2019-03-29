import requests

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
    url = 'https://dev34906.service-now.com/api/now/table/incident/' + sys_id + ''

    worknotes_update_response = requests.patch(url, auth=(user, pwd), headers=headers,
                                               json={"work_notes": work_notes})
    # Check for HTTP codes other than 200
    if worknotes_update_response.status_code != 200:
        print('Status:', worknotes_update_response.status_code, 'Headers:', worknotes_update_response.headers,
              'Error Response:', worknotes_update_response.json())
        exit()

    # Decode the JSON response into a dictionary and use the data

    data = worknotes_update_response.json()
    print(data)