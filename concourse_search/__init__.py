import sys
import re
import argparse
import subprocess


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
        return self._arguments.build

    def search(self):
        return self._arguments.search

    def chosen_command(self):
        return self


def parse_args(arguments):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    find_failures_parser = subparsers.add_parser('find-failures')
    find_failures_parser.add_argument('--target')
    find_failures_parser.add_argument('--pipeline')
    find_failures_parser.add_argument('--job')
    find_failures_parser.add_argument('--build')
    find_failures_parser.add_argument('--search')
    args = parser.parse_args(arguments)
    
    return FindFailuresArguments(args)


class FindMessageCommand():
    def find(self, target, job, build):
        full_command = [
            "fly",
            "--target", str(target),
            "watch",
            "--job", str(job),
            "--build", str(build)
        ]

        try:
            return subprocess.check_output(
                full_command
            ).splitlines(True)
        except subprocess.CalledProcessError as error:
            return error.output.splitlines(True)


def do_search(search, message):
    return search.search(message.decode('utf-8'))

        
class FindFailuresCommand():
    def __init__(self, find_message_command):
        self._find_message_command = find_message_command
        
    def find(self, target, build, job, search):
        reg = re.compile(r'%s' % search)
        
        results = [
            message
              for message
              in self._find_message_command.find(
                  target=target,
                  build=build,
                  job=job
              )
              if do_search(reg, message)
        ]
        
        return results
                
    
class Components():
    def __init__(self, stdout):
        self._stdout = stdout
        
    def stdout(self):
        return self._stdout

    def find_message_command(self):
        return FindMessageCommand()
        
        
def find_failures_runner(components, arguments):
    find_message_command = components.find_message_command()

    find_failures_command = FindFailuresCommand(
        find_message_command=find_message_command
    )

    for failure in find_failures_command.find(
        target=arguments.target(),
        build=arguments.build(),
        job=arguments.job(),
        search=arguments.search(),
    ):
        components.stdout().write(failure.decode('utf-8'))
    
    
def main(arguments, stdout=sys.stdout):
    runners = {
        'find-failures': find_failures_runner
    }
    parsed_arguments = parse_args(arguments)
    components = Components(stdout)
    runner = runners[parsed_arguments.chosen_command().name()]

    runner(components, parsed_arguments)
    
