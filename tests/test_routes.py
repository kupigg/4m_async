import unittest
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.v1 import router as v1_router
import utils.es as es_utils


class FakeESClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[tuple[str, dict]] = []

    async def search(self, index: str, body: dict) -> dict:
        self.calls.append((index, body))
        return self.payload


class RoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(v1_router, prefix="/api/v1")
        self.client = TestClient(app)

    def test_health_route(self) -> None:
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_ready_route_ok(self) -> None:
        with patch("api.v1.health.es_manager.ping", new=AsyncMock(return_value=True)), patch(
            "api.v1.health.redis_manager.ping", new=AsyncMock(return_value=True)
        ):
            response = self.client.get("/api/v1/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_ready_route_degraded(self) -> None:
        with patch("api.v1.health.es_manager.ping", new=AsyncMock(return_value=False)), patch(
            "api.v1.health.redis_manager.ping", new=AsyncMock(return_value=True)
        ):
            response = self.client.get("/api/v1/ready")

        self.assertEqual(response.status_code, 503)

    def test_films_route(self) -> None:
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": "524e4331-e14b-24d3-a156-426614174003",
                                "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
                                "imdb_rating": 9.4,
                            },
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get("/api/v1/films?sort=-imdb_rating&page_size=50&page_number=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["uuid"], "524e4331-e14b-24d3-a156-426614174003")

    def test_films_route_with_genre_filter(self) -> None:
        fake_client = FakeESClient({"hits": {"hits": []}})
        genre = "d007f2f8-4d45-4902-8ee0-067bae469161"

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get(f"/api/v1/films?genre={genre}&sort=-imdb_rating")

        self.assertEqual(response.status_code, 200)
        _, body = fake_client.calls[0]
        self.assertEqual(body["query"]["bool"]["filter"], [{"term": {"genres.id": genre}}])

    def test_films_route_with_invalid_sort(self) -> None:
        response = self.client.get("/api/v1/films?sort=-title")
        self.assertEqual(response.status_code, 422)

    def test_films_search_route(self) -> None:
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": "223e4317-e89b-22d3-f3b6-426614174000",
                                "title": "Billion Star Hotel",
                                "imdb_rating": 6.1,
                            }
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get("/api/v1/films/search/?query=star&page_number=1&page_size=50")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["title"], "Billion Star Hotel")
        _, body = fake_client.calls[0]
        self.assertEqual(body["query"]["multi_match"]["query"], "star")

    def test_film_detail_route(self) -> None:
        film_id = "b31592e5-673d-46dc-a561-9446438aea0f"
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": film_id,
                                "title": "Lunar: The Silver Star",
                                "imdb_rating": 9.2,
                                "description": "desc",
                                "genres": [{"id": "6f822a92-7b51-4753-8d00-ecfedf98a937", "name": "Action"}],
                                "actors": [{"id": "afbdbaca-04e2-44ca-8bef-da1ae4d84cdf", "full_name": "Ashley Parker Angel"}],
                                "writers": [{"id": "1bd9a00b-9596-49a3-afbe-f39a632a09a9", "full_name": "Toshio Akashi"}],
                                "directors": [{"id": "4a893a97-e713-4936-9dd4-c8ca437ab483", "full_name": "Toshio Akashi"}],
                            }
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get(f"/api/v1/films/{film_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["uuid"], film_id)
        self.assertEqual(response.json()["genre"][0]["name"], "Action")

    def test_persons_search_route(self) -> None:
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": "724e5631-e14b-14e3-a556-888814284902",
                                "full_name": "Captain Raju",
                                "films": [{"id": "eb055946-4841-4b83-9c32-14bb1bde5de4", "roles": ["actor"]}],
                            }
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get("/api/v1/persons/search/?query=captain&page_number=1&page_size=50")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["full_name"], "Captain Raju")

    def test_person_detail_route(self) -> None:
        person_id = "524e4331-e14b-24d3-a456-426614174002"
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": person_id,
                                "full_name": "George Lucas",
                                "films": [{"id": "eb055946-4841-4b83-9c32-14bb1bde5de4", "roles": ["writer"]}],
                            }
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get(f"/api/v1/persons/{person_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["uuid"], person_id)

    def test_person_films_route(self) -> None:
        person_id = "524e4331-e14b-24d3-a456-426614174002"
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": "524e4331-e14b-24d3-a456-426614174001",
                                "title": "Star Wars: Episode VI - Return of the Jedi",
                                "imdb_rating": 8.3,
                            }
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get(f"/api/v1/persons/{person_id}/film/?page_number=1&page_size=50")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["title"], "Star Wars: Episode VI - Return of the Jedi")
        _, body = fake_client.calls[0]
        self.assertEqual(body["query"]["term"]["persons.id"], person_id)

    def test_genres_route(self) -> None:
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": "d007f2f8-4d45-4902-8ee0-067bae469161",
                                "name": "Adventure",
                                "description": "Adventure genre",
                            },
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get("/api/v1/genres/?page_size=50&page_number=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Adventure")

    def test_genre_detail_route(self) -> None:
        genre_id = "aabbd3f3-f656-4fea-9146-63f285edf5c1"
        fake_client = FakeESClient(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": genre_id,
                                "name": "Action",
                                "description": "Action genre",
                            }
                        }
                    ]
                }
            }
        )

        with patch.object(es_utils.es_manager, "_client", fake_client):
            response = self.client.get(f"/api/v1/genres/{genre_id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["uuid"], genre_id)


if __name__ == "__main__":
    unittest.main()
