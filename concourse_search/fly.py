import subprocess
import yaml
import os


class FlyWatchResponse():
    def __init__(self, raw_lines, was_success):
        self._raw_lines = raw_lines
        self._was_success = was_success

    def raw_lines(self):
        return self._raw_lines

    def was_success(self):
        return self._was_success

    
class FlyTarget():
    def __init__(self, url, name):
        self._url = url
        self._name = name

    def url(self):
        return self._url

    def matches(self, name):
        return self._name == name

    
class FlyViaHttp():
    def targets(self):
        data = yaml.load(file(os.path.expanduser("~/.flyrc"), 'r'))
        targets = data.get('targets', {})
        return [
            FlyTarget(targets[key]['api'], key) for key in targets.keys()]

    def target_matching(self, target_name):
        for target in self.targets():
            if target.matches(target_name):
                return target

        raise RuntimeError("could not find base url for target: {target}".format(
            target=target_name
        ))
    
    def watch(self, target, pipeline, job, build):
        fly_target = self.target_matching(target)
        
        requests.get('{base_url}/{}'.format(
            base_url=fly_target.url(),
        ))
        
        return FlyWatchResponse(
            raw_lines=u'',
            was_success=True,
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

        raw_lines = None
        was_success = False

        try:
            raw_lines = subprocess.check_output(
                full_command
            )
            was_success = True
        
        except subprocess.CalledProcessError as error:
            raw_lines = error.output

        return FlyWatchResponse(
            raw_lines=raw_lines,
            was_success=was_success,
        )
        
    @staticmethod
    def _parse_target_line(line):
        for item in line.split(" "):
            if item.startswith("https"):
                return FlyTarget(url=item)
    