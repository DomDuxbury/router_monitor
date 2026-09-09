from datetime import UTC, datetime

from router.router_data import Data, DataDelta


def test_data_string_formats_byte_values():
    data = Data(downloaded_bytes=1234567, uploaded_bytes=987654)

    rendered = str(data)

    assert "downloaded_bytes=1.2Mb" in rendered
    assert "uploaded_bytes=987.7Kb" in rendered


def test_datadelta_updates_length_secs_from_timestamps():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 0, 30, tzinfo=UTC)

    delta = DataDelta(
        downloaded_bytes=10,
        uploaded_bytes=20,
        delta_start=start,
        delta_end=end,
    )

    assert delta.length_secs == 30.0
