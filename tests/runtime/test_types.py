import time

import pytest

from ..utils.utils import read_fixture
from turbine.runtime import Record
from turbine.runtime import RecordList
from turbine.runtime import Records


@pytest.fixture
def cdc_record():
    rec_json = read_fixture("tests/utils/json-record-cdc.json")
    return Record(key=rec_json["key"], value=rec_json["value"], timestamp=time.time())


@pytest.fixture
def non_cdc_record():
    rec_json = read_fixture("tests/utils/json-record-no-cdc.json")
    return Record(key=rec_json["key"], value=rec_json["value"], timestamp=time.time())


@pytest.fixture
def record_list():
    records = read_fixture("tests/utils/json-records-cdc.json")
    return RecordList(
        [
            Record(key=rec["key"], value=rec["value"], timestamp=time.time())
            for rec in records
        ]
    )


class TestRecord:
    def test_is_json_schema(self, cdc_record, non_cdc_record):
        assert cdc_record.is_json_schema is True
        assert non_cdc_record.is_json_schema is True

    def test_is_cdc_format(self, cdc_record, non_cdc_record):
        assert cdc_record.is_cdc_format is True
        assert non_cdc_record.is_cdc_format is False

    def test_unwrap_cdc_record(self, cdc_record):
        cdc_record.unwrap()
        assert "after" not in cdc_record.value["payload"]
        assert "before" not in cdc_record.value["payload"]
        assert "schema" in cdc_record.value

    def test_unwrap_non_cdc_record(self, non_cdc_record):
        before = non_cdc_record.value
        non_cdc_record.unwrap()
        assert before == non_cdc_record.value


class TestRecordList:
    def test_unwrap(self, record_list):
        record_list.unwrap()

        for rec in record_list.data:
            assert "after" not in rec.value["payload"]
            assert "before" not in rec.value["payload"]
            assert "schema" in rec.value


class TestRecords:
    def test_unwrap(self, record_list):
        recs = Records(records=record_list, stream="")
        recs.unwrap()

        for rec in recs.records:
            assert "after" not in rec.value["payload"]
            assert "before" not in rec.value["payload"]
            assert "schema" in rec.value
