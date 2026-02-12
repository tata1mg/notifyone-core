class AsyncTaskResponse:
    def __init__(self, data, meta=None, status_code=None, headers=None):
        self._data = data
        self._meta = meta
        self._status_code = status_code
        self._headers = headers

    @property
    def data(self):
        return self._data

    @property
    def meta(self):
        return self._meta

    @property
    def status(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers

    def __dict__(self):
        result = dict()
        result["data"] = self._data
        result["meta"] = self._meta
        result["headers"] = self._headers
        result["partial_complete"] = False
        result["is_success"] = True
        return result