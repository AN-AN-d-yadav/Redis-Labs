
import redis
import json

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

event = [{
    "event": "product_published",
    "product_id": 101,
    "name": "Mechanical Keyboard",
},{
   "event": "product_published",
   "product_id": 101,
   "name":"Electrical Piano"

}]

receivers = r.publish(
    "product-events",
    json.dumps(event),
)

print("Event published!")
print("Subscribers reached:", receivers)
