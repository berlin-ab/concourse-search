
def do_search(search, line):
    return search.search(line.message().decode('utf-8'))


class Line():
    def __init__(self, message):
        self._message = message

    def message(self):
        return self._message

    
class FindFailuresCommand():
    def __init__(self, find_message_command):
        self._find_message_command = find_message_command
        
    def find(self, target, build, job, search):
        results = []

        while (build > 0):
            results.extend(self._search(target, build, job, search))
            build = build - 1

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
