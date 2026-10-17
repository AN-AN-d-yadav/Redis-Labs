import redis
from redis.exceptions import WatchError

client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)

# Initial balance for this experiment
client.set("account:balance", 1000)

with client.pipeline() as tx:
    try:
        # Watch the key before reading it
        tx.watch("account:balance")

        balance = int(tx.get("account:balance"))
        print("Terminal A read balance:", balance)

        print("Now change the balance from Terminal B.")
        input("After Terminal B finishes, press Enter here...")

        # Start queuing transactional commands
        tx.multi()
        tx.set("account:balance", balance - 100)

        results = tx.execute()
        print("Transaction succeeded:", results)

    except WatchError:
        print("Transaction aborted! Balance changed by another client.")

print("Final balance:", client.get("account:balance"))