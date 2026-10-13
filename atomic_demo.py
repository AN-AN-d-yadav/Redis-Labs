
import redis
from concurrent.futures import ThreadPoolExecutor

r = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
)

r.set("lab:concurrent-counter", 0)


def increment():
    for _ in range(1000):
        value = int(r.get("lab:concurrent-counter"))
        r.set("lab:concurrent-counter", value + 1)


with ThreadPoolExecutor(max_workers=20) as pool:
    list(pool.map(lambda _: increment(), range(20)))

print(r.get("lab:concurrent-counter"))
