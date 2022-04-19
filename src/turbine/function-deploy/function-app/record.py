import json


class TurbineRecord:
    def __init__(self, record):
        self._raw_value = record.value
        self.key = record.key
        self.value = record.value
        self.timestamp = record.timestamp

    def deserialize(self):
        return self

    def serialize(self):
        return dict(
            key=self.key, value=json.dumps(self.value), timestamp=self.timestamp
        )
