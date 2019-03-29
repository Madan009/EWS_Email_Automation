import schedule

def schedule_job():

    schedule.every(5).seconds.do(extract_new_structured_email)
    schedule.every(5).seconds.do(follow_up)
    schedule.every(5).seconds.do(resolve_aws_incident)

while True:
    """
    This While loop should be there for scheduler to run!!!!
    """
    schedule.run_pending()
