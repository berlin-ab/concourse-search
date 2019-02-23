from concourse_search.domain import (
    Line,
    Build,
)


def transform_lines(lines, target, concourse_build):
    return [
        Line(
            team_name=concourse_build.team_name(),
            message=line,
            target=target,
            pipeline=concourse_build.pipeline(),
            job=concourse_build.job(),
            build=concourse_build.build_number(),
            base_url=concourse_build.base_url(),
        )
        for line
        in lines
    ]


def default_logger(message):
    pass


class BuildResponse():
    def __init__(self, lines, was_success, logfile_path):
        self._lines = lines
        self._was_success = was_success
        self._logfile_path = logfile_path

    def lines(self):
        return self._lines

    def was_success(self):
        return self._was_success

    def logfile_path(self):
        return self._logfile_path
        
        
class ConcourseBuild():
    def __init__(self, team_name, target, pipeline, job, build_number, base_url):
        self._target = target
        self._pipeline = pipeline
        self._job = job
        self._build_number = build_number
        self._base_url = base_url
        self._team_name = team_name

    def target(self):
        return self._target

    def pipeline(self):
        return self._pipeline

    def job(self):
        return self._job

    def build_number(self):
        return self._build_number

    def base_url(self):
        return self._base_url

    def team_name(self):
        return self._team_name
    
    def previous_build(self):
        return ConcourseBuild(
            team_name=self.team_name(),
            target=self.target(),
            pipeline=self.pipeline(),
            job=self.job(),
            build_number=self.build_number()-1,
            base_url=self.base_url(),
        )

    def previous_build_exists(self):
        return self.build_number() > 0

    
class ConcourseSearch():
    def __init__(self, fly, logger=default_logger):
        self.logger = logger
        self._fly = fly

    def find_builds(self, team_name, target, pipeline, job, starting_build_number, limit=100):
        base_url = self._fly.get_base_url(target)

        concourse_build = ConcourseBuild(
            team_name=team_name,
            target=target,
            pipeline=pipeline,
            job=job,
            build_number=starting_build_number,
            base_url=base_url,
        )
        
        result = []
        
        while (concourse_build.previous_build_exists() and limit > 0):
            response = self._fly.fetch(concourse_build)
            
            result.append(
                Build(
                    number=concourse_build.build_number(),
                    failing=(not response.was_success()),
                    pipeline=concourse_build.pipeline(),
                    job=concourse_build.job(),
                    base_url=concourse_build.base_url(),
                    logfile_path=response.logfile_path(),
                )
            )

            concourse_build = concourse_build.previous_build()
            limit = limit - 1

        return result
    
    def find(self, team_name, target, pipeline, job, build):
        self.logger("Searching for build number in : {build}, {job}".format(build=build, job=job))
        base_url = self._fly.get_base_url(target)

        concourse_build = ConcourseBuild(
            team_name=team_name,
            target=target,
            pipeline=pipeline,
            job=job,
            build_number=build,
            base_url=base_url
        )

        lines = self._fly.fetch(concourse_build).lines()

        return transform_lines(
            lines=lines,
            target=target,
            concourse_build=concourse_build,
        )

