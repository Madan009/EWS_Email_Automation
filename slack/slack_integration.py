import json
import requests

def post_in_slack(message,channel):

    # Set the webhook_url to the one provided by Slack when you create the webhook at https://my.slack.com/services/new/incoming-webhook/
    webhook_url = 'https://hooks.slack.com/services/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'
    slack_data = {'text': message}

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    return True