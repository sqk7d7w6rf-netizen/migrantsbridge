"""CSV and data export utilities."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Sequence

from pydantic import BaseModel


def _serialize_value(value: Any) -> str:
    """Convert a value to a CSV-safe string."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, dict)):
        import json
        return json.dumps(value, default=str)
    return str(value)


def export_to_csv(
    data: Sequence[dict[str, Any] | BaseModel],
    columns: list[str] | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    """Export a list of records to CSV string.

    Args:
        data: Sequence of dicts or Pydantic models.
        columns: Which fields to include (default: all from first record).
        headers: Mapping of field names to display headers.

    Returns:
        CSV content as a string.
    """
    if not data:
        return ""

    # Convert Pydantic models to dicts
    rows: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, BaseModel):
            rows.append(item.model_dump())
        else:
            rows.append(dict(item))

    if columns is None:
        columns = list(rows[0].keys())

    header_map = headers or {}
    display_headers = [header_map.get(col, col.replace("_", " ").title()) for col in columns]

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(display_headers)

    for row in rows:
        writer.writerow([_serialize_value(row.get(col)) for col in columns])

    return output.getvalue()


def export_to_csv_bytes(
    data: Sequence[dict[str, Any] | BaseModel],
    columns: list[str] | None = None,
    headers: dict[str, str] | None = None,
) -> bytes:
    """Export to CSV and return as UTF-8 bytes (for streaming response)."""
    csv_string = export_to_csv(data, columns, headers)
    return csv_string.encode("utf-8-sig")  # BOM for Excel compatibility


def generate_csv_response_headers(filename: str) -> dict[str, str]:
    """Generate HTTP headers for a CSV download response."""
    return {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
