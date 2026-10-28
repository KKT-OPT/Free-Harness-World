#!/usr/bin/env python3
"""Summarize structured latency records into cold, warmup, and steady phases."""

from __future__ import annotations

import argparse
import csv
import json
import math
import tempfile
from pathlib import Path
from typing import Any, Iterable


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "pass", "passed", "success"}:
        return True
    if normalized in {"false", "0", "no", "n", "fail", "failed", "error"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value!r}")


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            return [dict(row) for row in csv.DictReader(stream)]

    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("Input contains no records")

    if suffix == ".jsonl":
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        payload = json.loads(text)
        records = payload.get("records") if isinstance(payload, dict) else payload

    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ValueError("Input must be a JSON array, a JSON object with records, JSONL, or CSV")
    return records


def percentile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("Cannot calculate a percentile for an empty sample")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def round_number(value: float) -> float:
    return round(value, 6)


def summarize(records: Iterable[dict[str, Any]], latency_field: str, success_field: str) -> dict[str, Any]:
    latencies: list[float] = []
    success_count = 0
    for index, record in enumerate(records):
        if latency_field not in record:
            raise ValueError(f"Record {index} is missing latency field {latency_field!r}")
        latency = float(record[latency_field])
        if not math.isfinite(latency) or latency < 0:
            raise ValueError(f"Record {index} has invalid latency: {latency!r}")
        success = parse_bool(record.get(success_field, True))
        latencies.append(latency)
        success_count += int(success)

    if not latencies:
        return {
            "count": 0,
            "successCount": 0,
            "successRate": None,
            "total": None,
            "avg": None,
            "min": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "max": None,
        }

    ordered = sorted(latencies)
    count = len(latencies)
    total = sum(latencies)
    return {
        "count": count,
        "successCount": success_count,
        "successRate": round_number(success_count / count),
        "total": round_number(total),
        "avg": round_number(total / count),
        "min": round_number(ordered[0]),
        "p50": round_number(percentile(ordered, 0.50)),
        "p95": round_number(percentile(ordered, 0.95)),
        "p99": round_number(percentile(ordered, 0.99)),
        "max": round_number(ordered[-1]),
    }


def build_report(
    records: list[dict[str, Any]],
    latency_field: str,
    success_field: str,
    cold_count: int,
    warmup_count: int,
) -> dict[str, Any]:
    if cold_count < 0 or warmup_count < 0:
        raise ValueError("cold-count and warmup-count must be non-negative")
    if cold_count + warmup_count > len(records):
        raise ValueError("cold-count plus warmup-count exceeds the record count")

    cold_end = cold_count
    warmup_end = cold_end + warmup_count
    return {
        "schemaVersion": "harness.algorithmPerformanceSummary.v1",
        "latencyField": latency_field,
        "successField": success_field,
        "partition": {
            "coldCount": cold_count,
            "warmupCount": warmup_count,
            "steadyCount": len(records) - warmup_end,
        },
        "summary": {
            "all": summarize(records, latency_field, success_field),
            "cold": summarize(records[:cold_end], latency_field, success_field),
            "warmup": summarize(records[cold_end:warmup_end], latency_field, success_field),
            "steady": summarize(records[warmup_end:], latency_field, success_field),
        },
    }


def run_self_test() -> None:
    records = [
        {"elapsedMillis": 100, "success": True},
        {"elapsedMillis": 30, "success": True},
        {"elapsedMillis": 20, "success": False},
        {"elapsedMillis": 10, "success": True},
        {"elapsedMillis": 10, "success": True},
    ]
    report = build_report(records, "elapsedMillis", "success", cold_count=1, warmup_count=2)
    assert report["summary"]["cold"]["avg"] == 100
    assert report["summary"]["warmup"]["avg"] == 25
    assert report["summary"]["steady"]["avg"] == 10
    assert report["summary"]["all"]["successRate"] == 0.8

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        json_path = root / "records.json"
        json_path.write_text(json.dumps({"records": records}), encoding="utf-8")
        assert load_records(json_path) == records

        jsonl_path = root / "records.jsonl"
        jsonl_path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n",
            encoding="utf-8",
        )
        assert load_records(jsonl_path) == records

        csv_path = root / "records.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["elapsedMillis", "success"])
            writer.writeheader()
            writer.writerows(records)
        loaded_csv = load_records(csv_path)
        assert len(loaded_csv) == len(records)
        assert loaded_csv[0]["elapsedMillis"] == "100"
    print(json.dumps({"status": "passed", "mode": "self-test"}, ensure_ascii=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON, JSONL, or CSV latency records")
    parser.add_argument("--output", type=Path, help="Optional output JSON path")
    parser.add_argument("--latency-field", default="elapsedMillis")
    parser.add_argument("--success-field", default="success")
    parser.add_argument("--cold-count", type=int, default=1)
    parser.add_argument("--warmup-count", type=int, default=0)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if args.input is None:
        raise SystemExit("--input is required unless --self-test is used")

    report = build_report(
        load_records(args.input),
        args.latency_field,
        args.success_field,
        args.cold_count,
        args.warmup_count,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
