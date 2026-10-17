import redis
import time

client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)

client.flushdb()

client.set("otp:demo-user", "482913", ex=10)

print("Value:", client.get("otp:demo-user"))
print("TTL:", client.ttl("otp:demo-user"), "seconds")

time.sleep(11)

print("After expiry:", client.get("otp:demo-user"))
print("TTL after expiry:", client.ttl("otp:demo-user"))