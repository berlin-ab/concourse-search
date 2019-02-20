import subprocess
import os


from concourse_search.domain import Line


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


class ConcourseSearch():

    def __init__(self, logger=default_logger):
        self.logger = logger
                
    def find(self, target, pipeline, job, build):
        self.logger("Searching for build number: {build}".format(build=build))
        base_url = self._get_base_url(target)
        
        if not os.path.exists("/tmp/.concourse-search"):
            os.makedirs("/tmp/.concourse-search")

        logfile_path = "/tmp/.concourse-search/{target}-{pipeline}-{job}-{build}.log".format(
            target=target,
            pipeline=pipeline.replace("_", "-"),
            job=job.replace("_", "-").replace("/", "-"),
            build=build,
        )

        if not os.path.exists(logfile_path):
            raw_lines = self._fetch(target, job, build)
            with open(logfile_path, "wb") as logfile:
                logfile.write(raw_lines)
        else:
            with open(logfile_path, "rb") as file:
                raw_lines = file.read()

        return transform_lines(
            lines=raw_lines.splitlines(True),
            target=target,
            pipeline=pipeline,
            job=job,
            build=build,
            base_url=base_url
        )

    def _get_base_url(self, target):
        for line in subprocess.check_output(["fly", "targets"]).splitlines(True):
            if target in line:
                for item in line.split(" "):
                    if item.startswith("https"):
                        return item

        raise RuntimeError("could not find base url for target: {target}".format(target=target))

    def _fetch(self, target, pipeline, job, build):
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

        try:
            raw_lines = subprocess.check_output(
                full_command
            )
        except subprocess.CalledProcessError as error:
            raw_lines = error.output


        return raw_lines
        
