import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

import good_deed


def test_pick_deed_returns_string_from_correct_bucket():
    for bucket in good_deed.DEEDS:
        deed = good_deed.pick_deed(bucket)
        assert deed in good_deed.DEEDS[bucket]


def test_all_buckets_have_deeds():
    for bucket, deeds in good_deed.DEEDS.items():
        assert len(deeds) > 0, f"Bucket '{bucket}' has no deeds"


def test_load_log_returns_empty_list_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(good_deed, "LOG_FILE", tmp_path / "nonexistent.json")
    assert good_deed.load_log() == []


def test_load_log_returns_empty_list_on_corrupt_file(tmp_path, monkeypatch):
    log_file = tmp_path / "bad.json"
    log_file.write_text("not valid json")
    monkeypatch.setattr(good_deed, "LOG_FILE", log_file)
    assert good_deed.load_log() == []


def test_log_deed_writes_entry(tmp_path, monkeypatch):
    log_file = tmp_path / "deeds.json"
    monkeypatch.setattr(good_deed, "LOG_FILE", log_file)

    good_deed.log_deed("Help someone", "5m")

    log = json.loads(log_file.read_text())
    assert len(log) == 1
    assert log[0]["deed"] == "Help someone"
    assert log[0]["bucket"] == "5m"
    assert log[0]["done"] is False
    assert log[0]["date"] == str(date.today())


def test_log_deed_appends(tmp_path, monkeypatch):
    log_file = tmp_path / "deeds.json"
    monkeypatch.setattr(good_deed, "LOG_FILE", log_file)

    good_deed.log_deed("First deed", "30s")
    good_deed.log_deed("Second deed", "1h")

    log = json.loads(log_file.read_text())
    assert len(log) == 2


def test_mark_done_sets_flag(tmp_path, monkeypatch):
    log_file = tmp_path / "deeds.json"
    monkeypatch.setattr(good_deed, "LOG_FILE", log_file)

    good_deed.log_deed("Do something kind", "5m")
    good_deed.mark_done(0)

    log = json.loads(log_file.read_text())
    assert log[0]["done"] is True


def test_mark_done_ignores_invalid_index(tmp_path, monkeypatch, capsys):
    log_file = tmp_path / "deeds.json"
    monkeypatch.setattr(good_deed, "LOG_FILE", log_file)

    good_deed.log_deed("A deed", "30s")
    good_deed.mark_done(99)

    log = json.loads(log_file.read_text())
    assert log[0]["done"] is False
    captured = capsys.readouterr()
    assert "Invalid" in captured.out


def test_show_log_filters_by_days(tmp_path, monkeypatch):
    log_file = tmp_path / "deeds.json"
    monkeypatch.setattr(good_deed, "LOG_FILE", log_file)

    old_entry = {
        "date": str(date.today() - timedelta(days=10)),
        "bucket": "5m",
        "deed": "Old deed",
        "done": False,
    }
    recent_entry = {
        "date": str(date.today()),
        "bucket": "30s",
        "deed": "Recent deed",
        "done": True,
    }
    log_file.write_text(json.dumps([old_entry, recent_entry]))

    captured_output = []
    with patch("builtins.print", side_effect=lambda *a: captured_output.append(" ".join(str(x) for x in a))):
        good_deed.show_log(days=7)

    output = "\n".join(captured_output)
    assert "Recent deed" in output
    assert "Old deed" not in output


def test_bucket_labels_cover_all_deeds():
    for bucket in good_deed.DEEDS:
        assert bucket in good_deed.BUCKET_LABELS, f"Missing label for bucket '{bucket}'"
