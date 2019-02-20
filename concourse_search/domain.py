def do_search(search, line):
    return search.search(line.message().decode('utf-8'))


class Line():
    def __init__(self, message, job, target, build):
        self._message = message
        self._job = job
        self._target = target
        self._build = build

    def message(self):
        return self._message

    def job(self):
        return self._job

    def target(self):
        return self._target

    def build(self):
        return self._build

    
class FindFailuresCommand():
    def __init__(self, concourse_search):
        self._find_message_command = concourse_search
        
    def find(self, target, build, job, search, limit=100):
        results = []

        while (build > 0 and limit > 0):
            results.extend(self._search(target, build, job, search))
            build = build - 1
            limit = limit - 1

        return results

    def _search(self, target, build, job, search):
        results = []
        
        for line in self._find_message_command.find(
                  target=target,
                  build=build,
                  job=job
              ):

            if do_search(search, line):
                results.append(line)

        return results
