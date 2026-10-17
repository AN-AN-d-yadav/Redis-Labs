import redis

client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)

client.flushdb()

with client.pipeline(transaction=True) as tx:
    tx.set("account:balance", 1000)
    tx.incrby("account:balance", 500)
    tx.set("account:status", "active")

    results = tx.execute()

print("Transaction results:", results)
print("Balance:", client.get("account:balance"))
print("Status:", client.get("account:status"))