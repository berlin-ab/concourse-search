def matches_search_criteria(search, line):
    return search.search(line.message().decode('utf-8'))


class Line():
    def __init__(self, team_name, message, target, pipeline, job, build, base_url):
        self._team_name = team_name
        self._message = message
        self._target = target
        self._pipeline = pipeline
        self._job = job
        self._build = build
        self._base_url = base_url

    def team_name(self):
        return self._team_name

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


class Build():
    def __init__(self, number, failing, pipeline, job, base_url, logfile_path):
        self._number = number
        self._failing = failing
        self._pipeline = pipeline
        self._job = job
        self._base_url = base_url
        self._logfile_path = logfile_path

    def number(self):
        return self._number

    def is_failing(self):
        return self._failing

    def url(self):
        return u"{base_url}/teams/main/pipelines/{pipeline}/jobs/{job}/builds/{build}".format(
            base_url=self._base_url,
            pipeline=self._pipeline,
            job=self._job,
            build=self.number()
        )

    def logfile_path(self):
        return self._logfile_path
    
    
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


class FailingBuildsCommand():
    def __init__(self, concourse_search):
        self._concourse_search = concourse_search
    
    def find(self, team_name, target, pipeline, job, starting_build_number, limit):
        return [
            build
            for build
            in self._concourse_search.find_builds(team_name, target, pipeline, job, starting_build_number, limit)
            if build.is_failing()
        ]

    
class FindFailuresCommand():
    def __init__(self, concourse_search):
        self._find_message_command = concourse_search
        
    def find(self, team_name, target, build, pipeline, job, search, limit=100):
        failures_set = FailuresSet()

        while (build > 0 and limit > 0):
            for line in self._search(team_name, target, pipeline, build, job, search):
                failures_set.add(line)
                
            build = build - 1
            limit = limit - 1

        return failures_set.all()

    def _search(self, team_name, target, pipeline, build, job, search):
        lines = self._find_message_command.find(
            team_name=team_name,
            target=target,
            pipeline=pipeline,
            build=build,
            job=job
        )

        return [line
                for line
                in lines
                if matches_search_criteria(search, line)]
              
