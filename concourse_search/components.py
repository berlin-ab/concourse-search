import re


from concourse_search.domain import (
    FindFailuresCommand,
    FailingBuildsCommand,
)


from concourse_search.concourse import (
    ConcourseSearch,
    Fly,
)


class FailingBuildsArguments():
    def __init__(self, arguments):
        self._arguments = arguments

    def name(self):
        return 'failing-builds'

    def target(self):
        return self._arguments.target

    def pipeline(self):
        return self._arguments.pipeline

    def job(self):
        return self._arguments.job

    def starting_build(self):
        return self._arguments.starting_build
    
    def chosen_command(self):
        return self

    def verbose(self):
        return self._arguments.verbose

    def limit(self):
        return self._arguments.limit


class FindFailuresArguments():
    def __init__(self, arguments):
        self._arguments = arguments
        
    def name(self):
        return 'find-failures'

    def target(self):
        return self._arguments.target

    def pipeline(self):
        return self._arguments.pipeline

    def job(self):
        return self._arguments.job

    def build(self):
        return int(self._arguments.build)

    def search(self):
        return re.compile(self._arguments.search)

    def verbose(self):
        return self._arguments.verbose

    def limit(self):
        return self._arguments.limit

    def chosen_command(self):
        return self

    
class Components():
    def __init__(self, stdout, debug=False):
        self._stdout = stdout
        self.debug = debug
        
    def stdout(self):
        return self._stdout

    def logger(self, message):
        if self.debug is True:
            print(message)

    def fly(self):
        return Fly()

    def concourse_search(self):
        return ConcourseSearch(
            logger=self.logger,
            fly=self.fly()
        )

    def find_failures(self):
        return FindFailuresCommand(
            concourse_search=self.concourse_search()
        )

    def failing_builds(self):
        return FailingBuildsCommand(
            concourse_search=self.concourse_search()
        )

