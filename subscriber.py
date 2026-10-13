
import redis
import json

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

pubsub = r.pubsub()
pubsub.subscribe("product-events")

print("Subscriber started. Waiting for events...")

for message in pubsub.listen():
    if message["type"] == "message":
        event = json.loads(message["data"])
        print("Received event:", event)
