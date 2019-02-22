import os


from concourse_search.concourse import (
    BuildResponse,
)


class ConcourseSearchStorage():
    def __init__(self):
        self.ensure_storage_exists()
        
    def ensure_storage_exists(self):
        if not os.path.exists("/tmp/.concourse-search"):
            os.makedirs("/tmp/.concourse-search")

    def logfile_path(self, concourse_build):
        return "/tmp/.concourse-search/{target}-{pipeline}-{job}-{build}.log".format(
            target=concourse_build.target(),
            pipeline=concourse_build.pipeline().replace("_", "-"),
            job=concourse_build.job().replace("_", "-").replace("/", "-"),
            build=concourse_build.build_number(),
        )
    def success_file_path(self, concourse_build):
        return "/tmp/.concourse-search/{target}-{pipeline}-{job}-{build}-was-success.log".format(
            target=concourse_build.target(),
            pipeline=concourse_build.pipeline().replace("_", "-"),
            job=concourse_build.job().replace("_", "-").replace("/", "-"),
            build=concourse_build.build_number(),
        )

    def contains(self, concourse_build):
        return os.path.exists(self.logfile_path(concourse_build))

    def store(self, concourse_build, response):
        logfile_path = self.logfile_path(concourse_build)
        success_file_path = self.success_file_path(concourse_build)

        with open(logfile_path, "wb") as logfile:
            for line in response.lines():
                try:
                    logfile.write(line.encode('utf-8'))
                except UnicodeDecodeError as error:
                    logfile.write(line)

        if response.was_success():
            with open(success_file_path, "w") as logfile:
                logfile.write(u"true")

    def retrieve(self, concourse_build):
        logfile_path = self.logfile_path(concourse_build)
        success_file_path = self.success_file_path(concourse_build)
        
        with open(logfile_path, "rb") as file:
            lines = file.read().splitlines(True)
            
        was_success = os.path.exists(success_file_path)

        return BuildResponse(
            lines=lines,
            was_success=was_success,
            logfile_path=logfile_path,
        )

    
