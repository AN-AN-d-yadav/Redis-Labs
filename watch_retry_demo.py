# import redis
# from redis.exceptions import WatchError

# client = redis.Redis(
#     host="localhost",
#     port=6380,
#     decode_responses=True,
# )

# client.set("account:balance", 1000)

# def deduct(amount):
#     with client.pipeline() as tx:
#         while True:
#             try:
#                 tx.watch("account:balance")

#                 balance = int(tx.get("account:balance"))

#                 if balance < amount:
#                     tx.unwatch()
#                     return False

#                 tx.multi()
#                 tx.set("account:balance", balance - amount)
#                 tx.execute()

#                 return True

#             except WatchError:
#                 print("Balance changed concurrently. Retrying...")
#                 continue

# print("Before:", client.get("account:balance"))

# success = deduct(100)

# print("Deduction successful:", success)
# print("After:", client.get("account:balance"))

# lets create a conflict

import redis
from redis.exceptions import WatchError

client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)

client.set("account:balance", 1000)

def deduct(amount):
    with client.pipeline() as tx:
        attempt = 0

        while True:
            attempt += 1

            try:
                tx.watch("account:balance")

                balance = int(tx.get("account:balance"))
                print(f"Attempt {attempt}: read balance = {balance}")

                # Pause only on the first attempt for our demo
                if attempt == 1:
                    input("Change balance in Terminal B, then press Enter...")

                if balance < amount:
                    tx.unwatch()
                    return False

                tx.multi()
                tx.set("account:balance", balance - amount)
                tx.execute()

                print(f"Attempt {attempt}: transaction committed")
                return True

            except WatchError:
                print(f"Attempt {attempt}: conflict detected; retrying...")
                continue

print("Initial balance:", client.get("account:balance"))

success = deduct(100)

print("Deduction successful:", success)
print("Final balance:", client.get("account:balance"))