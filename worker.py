import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

# redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_url = os.getenv('REDISTOGO_URL', 'redis://h:p7f54ba08d713ff2365c6e5bf35eab18f1d223f4c5870767e5e083e97b27048f2@ec2-54-146-3-214.compute-1.amazonaws.com:24089')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()