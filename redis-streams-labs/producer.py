
import redis

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

events = [
    {"event": "order_created", "order_id": "101"},
    {"event": "order_created", "order_id": "102"},
    {"event": "order_created", "order_id": "103"},
]

for event in events:
    event_id = r.xadd("orders", event)
    print(f"Stored event: {event_id} -> {event}")
