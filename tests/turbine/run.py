# import time
import pytest

from turbine.src import TurbineClient

# from turbine.src import Record

# from ..utils.utils import read_fixture
# from turbine.runtime import RecordList
# from turbine.runtime import Records


@pytest.fixture()
def turibine_client():
    return TurbineClient(
        app_path="path_to_app",
    )


FIXTURES_PATH = "tests/utils/template-records.json"


class TestLocalResource:
    @pytest.mark.asyncio
    async def test_records(self):
        resource = turibine_client()

        records = await resource.records(
            git_sha="9435b35a23e43c2e5a9f0c118db257a88a5e1e01"
        )

        assert records.records is not None
        assert len(records.records.data) == 3

    @pytest.mark.asyncio
    async def test_write(self, capsys):
        resource = TurbineClient(name="name", fixtures_path=FIXTURES_PATH)

        records = await resource.records(collection="user_activity", config=None)

        await resource.write(rr=records, collection="user_activity")

        capture = capsys.readouterr()

        assert capture.out is not None
        assert capture.err == ""
