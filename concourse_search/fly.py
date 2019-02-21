import subprocess


class FlyWatchResponse():
    def __init__(self, lines, was_success):
        self._lines = lines
        self._was_success = was_success

    def lines(self):
        return self._lines

    def was_success(self):
        return self._was_success

    
class FlyTarget():
    def __init__(self, url):
        self._url = url

    def url(self):
        return self._url
    
    
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
                return self._parse_target_line(line)

        raise RuntimeError("could not find base url for target: {target}".format(target=target))

    def watch(self, target, pipeline, job, build):
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
    def _parse_target_line(line):
        for item in line.split(" "):
            if item.startswith("https"):
                return FlyTarget(url=item)
    
    
