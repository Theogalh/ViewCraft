def roster_job(ch, method, properties, body):
    data = body.decode('UTF-8').split(':')
