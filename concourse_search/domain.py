def do_search(search, line):
    return search.search(line.message().decode('utf-8'))


class Line():
    def __init__(self, message, target, pipeline, job, build, base_url):
        self._message = message
        self._target = target
        self._pipeline = pipeline
        self._job = job
        self._build = build
        self._base_url = base_url

    def message(self):
        return self._message

    def pipeline(self):
        return self._pipeline

    def job(self):
        return self._job

    def target(self):
        return self._target

    def build(self):
        return self._build

    def url(self):
        return u"{base_url}/teams/main/pipelines/{pipeline}/jobs/{job}/builds/{build}".format(
            base_url=self._base_url,
            pipeline=self.pipeline(),
            job=self.job(),
            build=self.build()
        )

    
class FailuresSet():

    def __init__(self):
        self._storage={}

    def add(self, line):
        key = "{build_number}|{text}".format(
            build_number=line.build(),
            text=line.message(),
        )
        
        self._storage[key] = line

    def all(self):
        return self._storage.values()

    
class FindFailuresCommand():
    def __init__(self, concourse_search):
        self._find_message_command = concourse_search
        
    def find(self, target, build, pipeline, job, search, limit=100):
        failures_set = FailuresSet()

        while (build > 0 and limit > 0):
            for line in self._search(target, pipeline, build, job, search):
                failures_set.add(line)
                
            build = build - 1
            limit = limit - 1

        return failures_set.all()

    def _search(self, target, pipeline, build, job, search):
        results = []

        lines = self._find_message_command.find(
            target=target,
            pipeline=pipeline,
            build=build,
            job=job
        )

        for line in lines:
            if do_search(search, line):
                results.append(line)
            
        return results
