import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', os.environ['REDIS_URL'])

conn = redis.from_url(redis_url)
print("worker connected " + str(conn))

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()