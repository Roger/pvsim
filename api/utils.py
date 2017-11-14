import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class JsonWrapper(object):
    @staticmethod
    def dumps(*args, **kwargs):
        return json.dumps(*args, cls=DateTimeEncoder, **kwargs)

    @staticmethod
    def loads(*args, **kwargs):
        return json.loads(*args, **kwargs)
