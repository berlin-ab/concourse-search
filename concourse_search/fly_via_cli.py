import subprocess


from concourse_search.fly import (
    FlyTarget,
    FlyBuildNotFound,
    FlyWatchResponse,
)


class FlyViaCli():
    def targets(self):
        return [
            line.decode('utf-8')
            for line
            in subprocess.check_output(["fly", "targets"]).splitlines(True)
        ]

    def target_matching(self, target):
        for line in self.targets():
            if target in line:
                return self._parse_target_line(line, target)

        raise RuntimeError("could not find base url for target: {target}".format(target=target))

    def watch(self, team_name, target, pipeline, job, build):
        full_command = [
            "fly",
            "--target", str(target),
            "watch",
            "--job", "{pipeline}/{job}".format(pipeline=pipeline, job=job),
            "--build", str(build)
        ]

        lines = None
        was_success = False

        try:
            lines = subprocess.check_output(
                full_command
            ).splitlines(True)
            was_success = True
        
        except subprocess.CalledProcessError as error:
            lines = error.output.splitlines(True)

        return FlyWatchResponse(
            lines=lines,
            was_success=was_success,
        )
        
    @staticmethod
    def _parse_target_line(line, target):
        for item in line.split(" "):
            if item.startswith("https"):
                return FlyTarget(
                    url=item,
                    name=target,
                )
    
