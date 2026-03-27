"""Defines utilities used for InfluxDB writing.

The main purpose of this module is to expose its structure-agnostic
'InfluxDBUtils.write_payload' function for writing MQTT payloads
into InfluxDB.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions

from config import InfluxDBConfig


def _to_datetime(time: str) -> datetime:
    """Parse ISO 8601 timestamp into UTC datetime.

    Args:
        time: Timestamp string from MQTT payload.

    Returns:
        Timezone-aware UTC datetime.
    """
    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)

    return dt.astimezone(UTC)


def _is_dict_of_fields(data: dict[str, Any]) -> bool:
    """Check if a Point should be created from a dictionary.

    Args:
        data: Dictionary of sub-dictionaries or fields.

    Returns:
        Whether a dictionary's values are all fields.
    """
    return all(isinstance(val, (int, float, bool)) for val in data.values())


def _create_point(
    measurement_name: str,
    tags: dict[str, str],
    fields: dict[str, Any],
    time: datetime,
) -> Point:
    """Create a Point object with the relevant attributes.

    Args:
        measurement_name: Name of measurement (usually name of the sensor).
        tags: Dictionary of tags for the measurement.
        fields: Dictionary of fields for the measurement
        time: Timestamp of measurement,

    Returns:
        Point object with tags, fields, and timestamp.
    """
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
    """Recursively extract Point objects from a payload tree.

    Args:
        node: Current node in the tree.
        time: Timestamp for all extracted Point objects (from base of payload).
        base_tags: Tags for all extracted Point objects (path from base of
            payload).
        path: Current traversal path within payload.

    Yields:
        Point objects derived from leaf dictionaries.
    """
    # Initialise path within payload
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


class InfluxDBUtils:
    """InfluxDB writing functionality."""

    def __init__(
        self,
        url: str = InfluxDBConfig.URL,
        token: str = InfluxDBConfig.TOKEN,
        org: str = InfluxDBConfig.ORG,
        write_options: WriteOptions = SYNCHRONOUS,
    ):
        """Initialise an InfluxDBUtils object.

        Args:
            url: URL to InfluxDB instance.
            token: InfluxDB API token.
            org: Organisation, this is a required parameter that is 'ignored'.
            write_options: Data writing behaviour.
        """
        self._write_api = InfluxDBClient(
            url=url,
            token=token,
            org=org,
        ).write_api(write_options=write_options)

    def _write_point(self, point: Point) -> None:
        """Write a Point object to InfluxDB.

        Args:
            point: The Point object to be written.
        """
        self._write_api.write(
            bucket=InfluxDBConfig.DATABASE,
            org=InfluxDBConfig.ORG,
            record=point,
        )

    def write_payload(self, payload: dict[str, Any]) -> None:
        """Write all Point objects yielded to InfluxDB.

        Args:
            payload: Dictionary from payload.
        """
        time = _to_datetime(payload["time"])
        device_id = payload["device_id"]

        base_tags = {"device_id": device_id}

        for point in _extract_points(payload, time, base_tags):
            self._write_point(point)
