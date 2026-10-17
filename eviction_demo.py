
# import redis
# import time

# # Connect to our disposable Redis container.
# # Host port 6380 maps to container port 6379.
# client = redis.Redis(
#     host="localhost",
#     port=6380,
#     decode_responses=True,
# )

# # Confirm that Redis is reachable.
# print("Redis connected:", client.ping())

# # Reset only this disposable lab's database.
# client.flushdb()

# # Capture initial eviction count.
# initial_evicted = int(client.info("stats")["evicted_keys"])

# print("Starting to insert keys...")

# # Insert many keys with moderately large values.
# # The 2 MB maxmemory limit should create memory pressure.
# value = "x" * 10_000

# for i in range(1, 2001):
#     client.set(f"eviction:key:{i}", value)

#     # Print occasional progress.
#     if i % 100 == 0:
#         print(f"Inserted {i} keys")

# # Inspect final Redis statistics.
# memory = client.info("memory")
# stats = client.info("stats")
# key_count = client.dbsize()
# final_evicted = int(stats["evicted_keys"])

# print("\n--- Results ---")
# print("Keys currently retained:", key_count)
# print("Memory used:", memory["used_memory_human"])
# print("Evicted keys during this run:", final_evicted - initial_evicted)
# print("Configured maxmemory:", client.config_get("maxmemory")["maxmemory"])
# print("Eviction policy:", client.config_get("maxmemory-policy")["maxmemory-policy"])



# one at a time -> this time with no eviction


import redis

client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True,
)

# Clear data only in our disposable lab Redis.
client.flushdb()

# Disable eviction for this experiment.
client.config_set("maxmemory-policy", "noeviction")

initial_evicted = int(client.info("stats")["evicted_keys"])
value = "x" * 10_000
successful_writes = 0

for i in range(1, 2001):
    try:
        client.set(f"noeviction:key:{i}", value)
        successful_writes += 1
    except redis.exceptions.ResponseError as error:
        print(f"Write failed at key {i}: {error}")
        break

stats = client.info("stats")

print("\n--- Results ---")
print("Successful writes:", successful_writes)
print("Keys currently retained:", client.dbsize())
print(
    "Keys evicted:",
    int(stats["evicted_keys"]) - initial_evicted,
)
print("Policy:", client.config_get("maxmemory-policy")["maxmemory-policy"])
