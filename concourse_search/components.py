import re


from concourse_search.domain import (
    FindFailuresCommand,
    FailingBuildsCommand,
)


from concourse_search.concourse import (
    ConcourseSearch,
)


from concourse_search.storage import (
    ConcourseSearchStorage
)


from concourse_search.fly import (
    CachingFlyClient,
)


from concourse_search.fly_via_cli import (
    FlyViaCli,
)


from concourse_search.fly_via_http import (
    FlyViaHttp,
)


class FailingBuildsArguments():
    def __init__(self, arguments):
        self._arguments = arguments

    def name(self):
        return 'failing-builds'

    def team_name(self):
        return "main"

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

    def team_name(self):
        return "main"

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
        return FlyViaHttp()

    def concourse_search_storage(self):
        return ConcourseSearchStorage(
            log_directory="/tmp/.concourse-search"
        )

    def caching_fly_client(self):
        return CachingFlyClient(
            storage=self.concourse_search_storage(),
            fly=self.fly(),
            logger=self.logger
        )

    def concourse_search(self):
        return ConcourseSearch(
            logger=self.logger,
            fly=self.caching_fly_client(),
        )

    def find_failures(self):
        return FindFailuresCommand(
            concourse_search=self.concourse_search()
        )

    def failing_builds(self):
        return FailingBuildsCommand(
            concourse_search=self.concourse_search()
        )

