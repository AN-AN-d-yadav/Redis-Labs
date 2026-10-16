
import redis

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

group = "email-workers"
consumer = "worker-1"
stream = "orders"

# Group se maximum 2 naye events read karo
results = r.xreadgroup(
    groupname=group,
    consumername=consumer,
    streams={stream: ">"},
    count=2,
    block=1000,
)

if not results:
    print("No new events available.")
else:
    for stream_name, messages in results:
        for event_id, fields in messages:
            print(f"Processing {event_id}: {fields}")

            # Yahan real application ka kaam hoga:
            # e.g. email notification bhejna

            # Processing successful hone ke baad acknowledge karo
            r.xack(stream_name, group, event_id)
            print(f"Acknowledged: {event_id}")
