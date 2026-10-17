import redis

client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)

client.set("account:balance", 1000)

# Terminal A reads the balance
balance = int(client.get("account:balance"))
print("Terminal A read:", balance)

input("Change the balance to 2000 in Terminal B, then press Enter...")

# Terminal A writes using its old value
client.set("account:balance", balance - 100)

print("Terminal A wrote:", balance - 100)
print("Final balance:", client.get("account:balance"))