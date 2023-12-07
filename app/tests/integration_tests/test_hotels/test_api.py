import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "location, date_from, date_to, status_code",
    [
        ("Алтай", "2023-06-15", "2023-06-11", 400),
        ("Алтай", "2023-06-15", "2023-07-20", 400),
        ("Алтай", "2023-04-15", "2023-04-20", 200),
    ],
)
async def test_get_hotel(location, date_from, date_to, status_code, ac: AsyncClient):
    query_params = {"date_from": date_from, "date_to": date_to}
    response = await ac.get(
        f"/hotels/{location}",
        params=query_params,
    )

    assert response.status_code == status_code
