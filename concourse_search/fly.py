        

class FlyWatchResponse():
    def __init__(self, lines, was_success):
        self._lines = lines
        self._was_success = was_success

    def lines(self):
        return self._lines

    def was_success(self):
        return self._was_success

    
class FlyTarget():
    def __init__(self, url, name, token=''):
        self._url = url
        self._token = token
        self._name = name

    def url(self):
        return self._url

    def matches(self, name):
        return self._name == name

    def token(self):
        return self._token

    
class FlyBuildNotFound(RuntimeError): pass

    
