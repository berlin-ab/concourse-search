import subprocess
import os


from concourse_search.domain import Line


def transform_lines(lines):
    return [Line(message=line) for line in lines]


class ConcourseSearch():
    def _fetch(self, target, job, build):
        full_command = [
            "fly",
            "--target", str(target),
            "watch",
            "--job", str(job),
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
        
    def find(self, target, job, build):
        if not os.path.exists("/tmp/.concourse-search"):
            os.makedirs("/tmp/.concourse-search")

        logfile_path = "/tmp/.concourse-search/{target}-{job}-{build}.log".format(
            target=target,
            job=job.replace("_", "-").replace("/", "-"),
            build=build,
        )

        if not os.path.exists(logfile_path):
            raw_lines = self._fetch(target, job, build)
            with open(logfile_path, "w") as logfile:
                logfile.write(raw_lines)
        else:
            with open(logfile_path, "r") as file:
                raw_lines = file.read()

        return transform_lines(raw_lines.splitlines(True))

