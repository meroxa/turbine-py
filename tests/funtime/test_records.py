import json

from turbine.function_deploy.function_app import service_pb2
from turbine.function_deploy.function_app.record import proto_records_to_turbine_records
from turbine.function_deploy.function_app.record import turbine_records_to_proto_records
from turbine.runtime import Record as TurbineRecord


class TestDecodeRecord:
    def test_proto_records_to_turbine_records_decode_json(self):
        in_record = service_pb2.Record(key="key", value=json.dumps("{}"), timestamp=0)

        out_record = proto_records_to_turbine_records(p_record=[in_record])

        assert out_record is not None
        assert out_record[0].key == "key"
        assert out_record[0].value == "{}"
        assert out_record[0].timestamp == 0

    def test_proto_records_to_turbine_records_decode_bytestring(self):

        test_string = "this is a test"
        in_record = service_pb2.Record(key="key", value=test_string, timestamp=0)

        out_record = proto_records_to_turbine_records(p_record=[in_record])

        assert out_record is not None
        assert out_record[0].key == "key"
        # the type has not been changed
        assert out_record[0].value == test_string
        assert out_record[0].timestamp == 0


class TestEncodeRecords:
    def test_turbine_records_to_proto_records_json(self):
        in_record = TurbineRecord(key="key", value=json.loads("{}"), timestamp=0)

        out_record = turbine_records_to_proto_records(t_record=[in_record])

        assert out_record is not None
        assert out_record[0].key == "key"
        assert out_record[0].value == "{}"
        assert out_record[0].timestamp == 0

    def test_turbine_records_to_proto_record_decode_bytestring(self):

        test_string = "test stuff"
        in_record = service_pb2.Record(key="key", value=test_string, timestamp=0)

        out_record = turbine_records_to_proto_records(t_record=[in_record])

        assert out_record is not None
        assert out_record[0].key == "key"
        assert out_record[0].value == json.dumps(test_string)
        assert out_record[0].timestamp == 0
