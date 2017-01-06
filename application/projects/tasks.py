from celery.task import task
import commands

@task(name="run_code")
def run_docker_cont(docker_run):
    status, output = commands.getstatusoutput(docker_run)
    return output
