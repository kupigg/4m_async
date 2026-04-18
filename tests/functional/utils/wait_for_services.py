import time
from collections.abc import Callable
from urllib.error import URLError
from urllib.request import urlopen

from elasticsearch import Elasticsearch
from redis import Redis

from tests.settings import FunctionalTestSettings, test_settings


def wait_for_service(
    name: str,
    check: Callable[[], bool],
    timeout: float,
    interval: float,
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if check():
                return
        except Exception:
            pass

        time.sleep(interval)

    raise TimeoutError(f"{name} is not available after {timeout} seconds")


def wait_for_elasticsearch(settings: FunctionalTestSettings = test_settings) -> None:
    es_client = Elasticsearch(hosts=settings.elasticsearch.url)
    wait_for_service(
        name="Elasticsearch",
        check=es_client.ping,
        timeout=settings.wait.timeout,
        interval=settings.wait.interval,
    )


def wait_for_redis(settings: FunctionalTestSettings = test_settings) -> None:
    redis_client = Redis.from_url(settings.redis.url)
    wait_for_service(
        name="Redis",
        check=redis_client.ping,
        timeout=settings.wait.timeout,
        interval=settings.wait.interval,
    )


def wait_for_api(settings: FunctionalTestSettings = test_settings) -> None:
    def check() -> bool:
        try:
            with urlopen(f"{settings.api.base_url}/api/v1/health", timeout=2) as response:
                return response.status == 200
        except (TimeoutError, URLError):
            return False

    wait_for_service(
        name="API",
        check=check,
        timeout=settings.wait.timeout,
        interval=settings.wait.interval,
    )


def wait_for_services(settings: FunctionalTestSettings = test_settings) -> None:
    wait_for_elasticsearch(settings)
    wait_for_redis(settings)
    wait_for_api(settings)


if __name__ == "__main__":
    wait_for_services()
