import subprocess


from concourse_search.domain import Line


def transform_lines(lines):
    return [Line(message=line) for line in lines]


class ConcourseSearch():
    def find(self, target, job, build):

        full_command = [
            "fly",
            "--target", str(target),
            "watch",
            "--job", str(job),
            "--build", str(build)
        ]

        try:
            return transform_lines(subprocess.check_output(
                full_command
            ).splitlines(True))
        except subprocess.CalledProcessError as error:
            return transform_lines(error.output.splitlines(True))

