import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

# redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_url = os.getenv('REDISTOGO_URL', 'redis://redistogo:e427beb4e2074dc3f38b1cda72f2413e@pike.redistogo.com:11994/')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()