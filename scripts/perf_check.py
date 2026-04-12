import argparse
import asyncio
import statistics
import time

import httpx


async def one_request(client: httpx.AsyncClient, path: str) -> float:
    start = time.perf_counter()
    response = await client.get(path)
    response.raise_for_status()
    return (time.perf_counter() - start) * 1000


async def run(base_url: str, path: str, total: int, concurrency: int) -> list[float]:
    sem = asyncio.Semaphore(concurrency)
    latencies: list[float] = []

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        async def worker() -> None:
            async with sem:
                latencies.append(await one_request(client, path))

        await asyncio.gather(*(worker() for _ in range(total)))

    return latencies


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = int((len(values) - 1) * p)
    return values[index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple latency smoke-check for API endpoint")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--path", default="/api/v1/films?sort=-imdb_rating&page_size=50&page_number=1")
    parser.add_argument("--total", type=int, default=2000)
    parser.add_argument("--concurrency", type=int, default=200)
    args = parser.parse_args()

    latencies = asyncio.run(run(args.base_url, args.path, args.total, args.concurrency))
    p95 = percentile(latencies, 0.95)

    print(f"requests={len(latencies)}")
    print(f"avg_ms={statistics.mean(latencies):.2f}")
    print(f"p95_ms={p95:.2f}")
    print(f"max_ms={max(latencies):.2f}")

    if p95 > 200:
        raise SystemExit("FAIL: p95 > 200ms")

    print("OK: p95 <= 200ms")


if __name__ == "__main__":
    main()
