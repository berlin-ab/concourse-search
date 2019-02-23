import os
import yaml
import logging
import requests
import json
import sseclient


from concourse_search.fly import (
    FlyTarget,
    FlyBuildNotFound,
    FlyWatchResponse,
)


logging.getLogger('sseclient').setLevel(logging.INFO)


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
    
    def watch(self, team_name, target, pipeline, job, build):
        fly_target = self.target_matching(target)

        response = requests.get('{base_url}/api/v1/teams/{team_name}/pipelines/{pipeline}/jobs/{job}/builds/{build}'.format(
            team_name=team_name,
            base_url=fly_target.url(),
            pipeline=pipeline,
            job=job,
            build=build,
        ))

        if response.status_code != 200:
            raise FlyBuildNotFound(target, pipeline, job, build)

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

    
