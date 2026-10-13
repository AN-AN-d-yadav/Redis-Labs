
import redis
from time import perf_counter

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

# Individual commands
start = perf_counter()

for i in range(1000):
    r.set(f"lab:pipeline:{i}", i)

individual_time = perf_counter() - start

# Pipeline commands
pipe = r.pipeline(transaction=False)

start = perf_counter()

for i in range(1000):
    pipe.set(f"lab:pipeline:{i}", i)

pipe.execute()

pipeline_time = perf_counter() - start

print("Individual:", round(individual_time * 1000, 2), "ms")
print("Pipeline:", round(pipeline_time * 1000, 2), "ms")
