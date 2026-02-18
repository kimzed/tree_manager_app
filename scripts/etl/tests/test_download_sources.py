from unittest.mock import patch, MagicMock

import httpx
import pytest

from scripts.etl.download_sources import download_file


def test_download_raises_on_http_error(tmp_path):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404),
    )
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("scripts.etl.download_sources.httpx.stream", return_value=mock_response):
        with pytest.raises(httpx.HTTPStatusError):
            download_file("https://example.com/bad", tmp_path / "out.zip", "Test")
