# create consumer group
import redis

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

try:
    r.xgroup_create(
        name="orders",
        groupname="email-workers",
        id="0",
        mkstream=True,
    )
    print("Consumer group created!")

except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" in str(e):
        print("Consumer group already exists.")
    else:
        raise
