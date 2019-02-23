        

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


def default_logger(message):
    pass


class ConcourseBaseUrlFinder():
    def __init__(self, fly):
        self._cache = {}
        self._fly = fly
        
    def find(self, target):
        return self._cache.get(target, self._fetch(target))

    def _fetch(self, target):
        fly_target = self._fly.target_matching(target)
        self._cache[target] = fly_target.url()
        return fly_target.url()

    
class CachingFlyClient():
    def __init__(self, storage, fly, logger=default_logger):
        self._logger = logger
        self._storage = storage
        self._concourse_base_url_finder = ConcourseBaseUrlFinder(fly)
        self._fly = fly

    def fetch(self, concourse_build):
        if not self._storage.contains(concourse_build):
            response = self._fetch_log_from_fly(concourse_build)
            self._storage.store(concourse_build, response)
            
        return self._storage.retrieve(concourse_build)

    def target_matching(self, target_name):
        return self._fly.target_matching(target_name)

    def get_base_url(self, target):
        return self._concourse_base_url_finder.find(target)
    
    def _fetch_log_from_fly(self, concourse_build):
        self._logger("Searching concourse for build number: {build}".format(
            build=concourse_build.build_number()
        ))
        
        return self._fly.watch(
            team_name=concourse_build.team_name(),
            target=concourse_build.target(),
            pipeline=concourse_build.pipeline(),
            job=concourse_build.job(),
            build=concourse_build.build_number(),
        )
    
