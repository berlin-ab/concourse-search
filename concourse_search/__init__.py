import sys
import re
import argparse


from concourse_search.domain import (
    FindFailuresCommand,
)


from concourse_search.concourse import (
    ConcourseSearch
)


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


def parse_args(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action='store_true')
    subparsers = parser.add_subparsers(dest="chosen_command")
    find_failures_parser = subparsers.add_parser('find-failures')
    find_failures_parser.add_argument('--target')
    find_failures_parser.add_argument('--pipeline')
    find_failures_parser.add_argument('--job')
    find_failures_parser.add_argument('--build', type=int)
    find_failures_parser.add_argument('--search')
    find_failures_parser.add_argument('--limit', default=100, type=int)
    args = parser.parse_args(arguments)

    if args.chosen_command == 'find-failures':
        return FindFailuresArguments(args)
    else:
        print("Unknown command")
        exit(1)


class Components():
    def __init__(self, stdout, debug=False):
        self._stdout = stdout
        self.debug = debug
        
    def stdout(self):
        return self._stdout

    def logger(self, message):
        if self.debug is True:
            print(message)

    def concourse_search(self):
        return ConcourseSearch(logger=self.logger)

    def find_failures(self):
        return FindFailuresCommand(
            concourse_search=self.concourse_search()
        )

    
def display_failure_as_row(failure, stdout):
    stdout.write(u"{build_number} | {message}".format(
        build_number=failure.build(),
        message=failure.message().decode('utf-8')
    ))
    
        
def find_failures_runner(components, arguments):
    for failure in components.find_failures().find(
        target=arguments.target(),
        build=arguments.build(),
        pipeline=arguments.pipeline(),
        job=arguments.job(),
        search=arguments.search(),
        limit=arguments.limit(),
    ):
        display_failure_as_row(failure, components.stdout())
    
    
def main(arguments, stdout=sys.stdout):
    runners = {
        'find-failures': find_failures_runner
    }
    
    parsed_arguments = parse_args(arguments)
    components = Components(stdout, parsed_arguments.verbose())
    runner = runners[parsed_arguments.chosen_command().name()]

    if runner:
        runner(components, parsed_arguments)
    else:
        print("Unknown command")
        
