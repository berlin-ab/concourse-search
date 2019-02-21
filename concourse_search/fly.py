import subprocess
import yaml
import os
import requests
import json
import sseclient
import logging


logging.getLogger('sseclient').setLevel(logging.INFO)
        

class FlyWatchResponse():
    def __init__(self, lines, was_success):
        self._lines = lines
        self._was_success = was_success

    def lines(self):
        return self._lines

    def was_success(self):
        return self._was_success

    
class FlyTarget():
    def __init__(self, url, name, token=''):
        self._url = url
        self._token = token
        self._name = name

    def url(self):
        return self._url

    def matches(self, name):
        return self._name == name

    def token(self):
        return self._token

    
class FlyViaHttp():
    def __init__(self, session=requests.Session()):
        with open(os.path.expanduser("~/.flyrc"), 'r') as file:
            self._data = yaml.load(file.read())
        self._session = session
        
    def targets(self):
        targets = self._data.get('targets', {})
        
        return [
            FlyTarget(
                targets[key].get('api', {}),
                key,
                targets[key].get('token', {}).get('value'),
            ) for key in targets.keys()
        ]

    def target_matching(self, target_name):
        for target in self.targets():
            if target.matches(target_name):
                return target

        raise RuntimeError("could not find base url for target: {target}".format(
            target=target_name
        ))
    
    def watch(self, target, pipeline, job, build):
        fly_target = self.target_matching(target)

        response = requests.get('{base_url}/api/v1/teams/main/pipelines/{pipeline}/jobs/{job}/builds/{build}'.format(
            base_url=fly_target.url(),
            pipeline=pipeline,
            job=job,
            build=build,
        ))

        events_path = response.json()['api_url']
        events = []
        
        response = requests.get('{base_url}/{events_path}/events'.format(
            base_url=fly_target.url(),
            events_path=events_path
        ), headers={
            'Authorization': 'Bearer {bearer_token}'.format(
                bearer_token=fly_target.token()
            )
        }, stream=True)
        
        client = sseclient.SSEClient(response)
        was_success = False

        for line in client.events():
            if line.data:
                data = json.loads(line.data)

            if data["data"].get("status") in ["succeeded"]:
                was_success = True
                break
            elif data["data"].get("status") in ["failed", "errored", "aborted"]:
                events.append(data)
                break
            elif data["data"].get("status") not in [None, "started"]:
                pass
                # nothing
            else:
                events.append(data)
                
        return FlyWatchResponse(
            lines=[event.get(u"data", {}).get(u"payload", u"") for event in events],
            was_success=was_success,
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
                return FlyTarget(url=item, name='')
    
