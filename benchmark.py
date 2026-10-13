
import time
import statistics
import httpx

# ---BENCHMARK CONFIGURATION---
API_URL = "http://127.0.0.1:8001/v1/datasets"
REQUEST_COUNT = 5

payload = {
    "clients": 100,
    "employees": 20,
    "history_months": 12,
    "seed": 42
}

# ---RUN SEQUENTIAL REQUESTS---
latencies = []
successful = 0

start = time.perf_counter()

with httpx.Client(timeout=60.0) as client:
    for i in range(REQUEST_COUNT):
        request_start = time.perf_counter()

        response = client.post(API_URL, json=payload)

        elapsed = time.perf_counter() - request_start
        latencies.append(elapsed)

        if response.status_code == 201:
            successful += 1

        print(
            f"Request {i + 1}: "
            f"HTTP {response.status_code} | "
            f"{elapsed:.3f} seconds"
        )

total_seconds = time.perf_counter() - start

# ---PERFORMANCE METRICS---
print("\n---BENCHMARK RESULTS---")
print(f"Successful requests: {successful}/{REQUEST_COUNT}")
print(f"Average latency: {statistics.mean(latencies):.3f} seconds")
print(f"Median latency: {statistics.median(latencies):.3f} seconds")
print(f"Total elapsed time: {total_seconds:.3f} seconds")
print(f"Throughput: {successful / total_seconds * 60:.2f} datasets/minute")
