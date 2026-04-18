import aiohttp


async def assert_status(
    session: aiohttp.ClientSession,
    path: str,
    expected_status: int,
) -> dict | list:
    async with session.get(path) as response:
        payload = await response.json()
        assert response.status == expected_status, payload
        return payload
