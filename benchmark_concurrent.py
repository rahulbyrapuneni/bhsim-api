
import time
import statistics
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---BENCHMARK CONFIGURATION---
API_URL = "http://127.0.0.1:8001/v1/datasets"
REQUEST_COUNT = 5

payload = {
    "clients": 100,
    "employees": 20,
    "history_months": 12,
    "seed": 42
}

# ---SEND ONE REQUEST---
def generate_dataset(request_number):
    start = time.perf_counter()

    try:
        response = httpx.post(
            API_URL,
            json=payload,
            timeout=60.0
        )

        elapsed = time.perf_counter() - start

        return {
            "request": request_number,
            "status": response.status_code,
            "latency": elapsed
        }

    except httpx.RequestError as error:
        return {
            "request": request_number,
            "status": "ERROR",
            "latency": time.perf_counter() - start,
            "error": str(error)
        }

# ---RUN CONCURRENT REQUESTS---
print("Sending 5 concurrent requests...")

start = time.perf_counter()
results = []

with ThreadPoolExecutor(max_workers=REQUEST_COUNT) as executor:
    futures = [
        executor.submit(generate_dataset, i + 1)
        for i in range(REQUEST_COUNT)
    ]

    for future in as_completed(futures):
        results.append(future.result())

total_seconds = time.perf_counter() - start

# ---PERFORMANCE RESULTS---
results.sort(key=lambda result: result["request"])

for result in results:
    print(
        f"Request {result['request']}: "
        f"HTTP {result['status']} | "
        f"{result['latency']:.3f} seconds"
    )
    if "error" in result:
        print(f"  Error: {result['error']}")

successful = sum(result["status"] == 201 for result in results)
latencies = [result["latency"] for result in results]

print("\n---CONCURRENT BENCHMARK RESULTS---")
print(f"Successful requests: {successful}/{REQUEST_COUNT}")
print(f"Average latency: {statistics.mean(latencies):.3f} seconds")
print(f"Median latency: {statistics.median(latencies):.3f} seconds")
print(f"Total elapsed time: {total_seconds:.3f} seconds")
print(f"Throughput: {successful / total_seconds * 60:.2f} datasets/minute")
