import pytest
import requests

from drama_tracker import app
from drama_tracker.secrets import MOVIE_DB_API_KEY


@pytest.fixture
def avengers_args():
    return {
        "Content Type": [{"text": "movie"}],
        "Title": [{"text": "Avengers"}],
        "Language": {"name": "en"},
    }


@pytest.fixture
def avengers_result():
    return {
        "results": [
            {
                "adult": False,
                "backdrop_path": "/nNmJRkg8wWnRmzQDe2FwKbPIsJV.jpg",
                "genre_ids": [878, 28, 12],
                "id": 24428,
                "original_language": "en",
                "original_title": "The Avengers",
            }
        ]
    }


def test_get_title_details(mocker, avengers_args, avengers_result):
    mock_api_call = mocker.patch("requests.get", return_value=requests.Response())
    mock_jsonify = mocker.patch("requests.Response.json", return_value=avengers_result)
    app.get_title_details(avengers_args)

    request_url = f"https://api.themoviedb.org/3/search/movie?api_key={MOVIE_DB_API_KEY}&language=en&query=Avengers"  # noqa: E501
    mock_api_call.assert_called_with(request_url)
    mock_jsonify.assert_called_once()
