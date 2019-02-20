import subprocess
import os


from concourse_search.domain import (
    Line,
    Build,
)


def transform_lines(lines, target, pipeline, job, build, base_url):
    return [
        Line(
            message=line,
            target=target,
            pipeline=pipeline,
            job=job,
            build=build,
            base_url=base_url,
        )
        for line
        in lines
    ]


def default_logger(message):
    pass


class Response():
    def __init__(self, raw_lines, was_success, logfile):
        self._raw_lines = raw_lines
        self._was_success = was_success
        self._logfile = logfile

    def raw_lines(self):
        return self._raw_lines

    def was_success(self):
        return self._was_success

    def logfile_path(self):
        return self._logfile

    
class ConcourseBaseUrlFinder():
    def __init__(self):
        self._cache = {}
        
    def find(self, target):
        return self._cache.get(target, self._fetch(target))

    def _fetch(self, target):
        for line in subprocess.check_output(["fly", "targets"]).splitlines(True):
            decoded_line=line.decode('utf-8')
            if target in decoded_line:
                for item in decoded_line.split(" "):
                    if item.startswith("https"):
                        self._cache[target] = item
                        return item

        raise RuntimeError("could not find base url for target: {target}".format(target=target))

    
class ConcourseSearch():

    def __init__(self, logger=default_logger):
        self.logger = logger
        self.concourse_base_url_finder = ConcourseBaseUrlFinder()

    def find_builds(self, target, pipeline, job, starting_build_number, limit=100):
        result = []
        base_url = self._get_base_url(target)
        
        while (starting_build_number > 0 and limit > 0):
            response = self._fetch(target, pipeline, job, starting_build_number)
            result.append(
                Build(
                    number=starting_build_number,
                    failing=(not response.was_success()),
                    pipeline=pipeline,
                    job=job,
                    base_url=base_url,
                    logfile_path=response.logfile_path(),
                )
            )
            starting_build_number = starting_build_number - 1
            limit = limit - 1

        return result
    
    def find(self, target, pipeline, job, build):
        self.logger("Searching for build number: {build}".format(build=build))

        base_url = self._get_base_url(target)
        raw_lines = self._fetch(target, pipeline, job, build).raw_lines()

        return transform_lines(
            lines=raw_lines.splitlines(True),
            target=target,
            pipeline=pipeline,
            job=job,
            build=build,
            base_url=base_url
        )

    def _get_base_url(self, target):
        return self.concourse_base_url_finder.find(target)
    
    def _fetch(self, target, pipeline, job, build):
        if not os.path.exists("/tmp/.concourse-search"):
            os.makedirs("/tmp/.concourse-search")

        logfile_path = "/tmp/.concourse-search/{target}-{pipeline}-{job}-{build}.log".format(
            target=target,
            pipeline=pipeline.replace("_", "-"),
            job=job.replace("_", "-").replace("/", "-"),
            build=build,
        )
        
        success_file_path = "/tmp/.concourse-search/{target}-{pipeline}-{job}-{build}-was-success.log".format(
            target=target,
            pipeline=pipeline.replace("_", "-"),
            job=job.replace("_", "-").replace("/", "-"),
            build=build,
        )

        if not os.path.exists(logfile_path):
            response = self._do_fetch(target, pipeline, job, build)
            
            with open(logfile_path, "wb") as logfile:
                logfile.write(response.raw_lines())

            if response.was_success():
                with open(success_file_path, "w") as logfile:
                    logfile.write(u"true")

            return response
        else:
            with open(logfile_path, "rb") as file:
                raw_lines = file.read()

            was_success =  os.path.exists(success_file_path)

            return Response(
                raw_lines=raw_lines,
                was_success=was_success,
                logfile=logfile_path,
            )

    def _do_fetch(self, target, pipeline, job, build):
        self.logger("Searching concourse for build number: {build}".format(
            build=build
        ))
        
        full_command = [
            "fly",
            "--target", str(target),
            "watch",
            "--job", "{pipeline}/{job}".format(pipeline=pipeline, job=job),
            "--build", str(build)
        ]

        raw_lines = None
        was_success = False

        try:
            raw_lines = subprocess.check_output(
                full_command
            )
            was_success = True
        
        except subprocess.CalledProcessError as error:
            raw_lines = error.output

        return Response(
            raw_lines=raw_lines,
            was_success=was_success,
        )


        
