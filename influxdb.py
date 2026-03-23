"""influxdb.py

Defines framework used for InfluxDB writing.
"""

import json
from datetime import datetime, timezone
from typing import Any, Iterator
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import InfluxDBConfig

# Create InfluxDB client with synchronous writing API
client = InfluxDBClient(
    url=InfluxDBConfig.URL,
    token=InfluxDBConfig.TOKEN,
    org=InfluxDBConfig.ORG,
)
write_api = client.write_api(write_options=SYNCHRONOUS)


def _parse_time(time: str) -> datetime:
    """Return datetime frome MQTT publisher timestamp."""

    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def _is_dict_of_fields(data: dict[str, Any]) -> bool:
    """Return whether a dictionary's values are all fields."""

    return all(isinstance(val, (int, float, bool)) for val in data.values())


def _create_point(
    measurement_name: str,
    tags: dict[str, str],
    fields: dict[str, Any],
    time: datetime,
) -> Point:
    """Return a Point object with tags, fields, and a timestamp."""

    point = Point(measurement_name)

    for key, value in tags.items():
        point = point.tag(key, value)

    for key, value in fields.items():
        point = point.field(key, value)

    point.time(time)

    return point


def _extract_points(
    node: dict[str, Any],
    time: datetime,
    base_tags: dict[str, str],
    path: list[str] | None = None,
) -> Iterator[Point]:
    """Recursively traverse payload and return an Interator over Points upon every encounter of a dictionary of fields."""

    # Initialise location (path) within payload
    if path is None:
        path = []

    for key, val in node.items():
        if not isinstance(val, dict):
            continue

        # Record path
        current_path = path + [key]

        # Add point to Iterator if it is a dictionary of fields
        if _is_dict_of_fields(val):
            measurement_name = current_path[-1]
            tags = dict(base_tags)
            fields = val

            if len(current_path) >= 3 and current_path[-3] == "sensor_levels":
                tags["level"] = current_path[-2]

            yield _create_point(measurement_name, tags, fields, time)

        # Extract all points from sub-dictionary
        else:
            yield from _extract_points(
                val,
                time,
                base_tags,
                path=current_path,
            )


def _write_point(point: Point) -> None:
    """Write a point to InfluxDB."""

    write_api.write(
        bucket=InfluxDBConfig.DATABASE,
        org=InfluxDBConfig.ORG,
        record=point,
    )


def _write_payload(payload: dict[str, Any]) -> None:
    """Write all points to InfluxDB."""

    time = _parse_time(payload["time"])
    device_id = payload["device_id"]

    base_tags = {"device_id": device_id}

    for point in _extract_points(payload, time, base_tags):
        _write_point(point)


def write_payload_from_message(message: str) -> None:
    """Write payload data to InfluxDB from message."""

    payload = json.loads(message.payload.decode("utf-8"))
    _write_payload(payload)
