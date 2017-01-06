"""Receive input from the front-end, run code, collect and return stats"""

from django.http import JsonResponse
import json
import os
import uuid
import commands
import time

from quickrun.tasks import run_docker_cont

def staticAnalView(request):
    """
    Receive some input in JSON format,
    decode it, call the correct handler method,
    return static results
    """
    data = json.loads(request.body)

    location = write_files(data, 'static')
    path = os.environ['HOST_PATH'] + '/' + location[0]
    output = ([], '')

    build_static_container(path, location[1])

    language = data['info']['language']
    title = data['info']['title']

    status = 0
    output = []

    command = 'docker run --rm -v ' + path + ':/app -w /app static-tools '

    if language == 'Java':
        command = command + 'java -jar /usr/src/app/checkstyle-6.13-all.jar -c /usr/src/app/google_std.xml '
        docker_run = command + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        if status != 0:
            new_output = []
            error = 'Caused by: /usr/src/app'
            for line in output:
                if error in line:
                    new_output.append(line)
            output = new_output
    elif language == 'Python':
        docker_run = command + 'pylint --reports=n ' + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        output.pop(0)
    elif language == 'C++':
        docker_run = command + 'cpplint ' + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    elif language == 'ObjectiveC':
        docker_run = command + 'oclint ' + title + ' -- -c'
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    elif language == 'Golang':
        go_vet = command + 'go vet ' + title
        status, output = commands.getstatusoutput(go_vet)
        output_vet = output.split('\n')

        if(output_vet[0] == '' and len(output_vet) == 1):
            output_vet = ['All good.']

        go_lint = command + 'golint ' + title
        status, output = commands.getstatusoutput(go_lint)
        output_lint = output.split('\n')
        if(output_lint[0] == '' and len(output_lint) == 1):
            output_lint = ['All good.']

        output = ['Coding correctness.'] + output_vet \
                + ['---------------------------'] \
                + ['Coding style.'] + output_lint
    elif language == 'Bash':
        docker_run = command + '/root/.cabal/bin/shellcheck ' + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        if(output[0] == '' and len(output) == 1):
            output = ['All good.']
    elif language == 'Perl':
        docker_run = command + 'perlcritic -3 ' + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    elif language == 'Ruby':
        docker_run = command + 'ruby-lint ' + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        if(output[0] == '' and len(output) == 1):
            output = ['All good.']
    elif language == 'Scala':
        docker_run = command + 'java -jar /usr/src/app/scalastyle_2.10-0.8.0-batch.jar --config /usr/src/app/scalastyle_config.xml ' + title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    else:
        output = [title + " File type not supported"]
        status = -1

    ret = {'output': output}

    os.system('rm -rf ' + location[0])
    return JsonResponse(ret)

def build_static_container(path, tag):
    """Build the container used for the static analysis"""
    docker_build = 'docker build -t ' + tag + ' ' + path + '.'
    commands.getstatusoutput(docker_build)

def singleRunView(request):
    """
    Receive some input in JSON format,
    decode it, call the correct handler method,
    retrieve stats and return results.
    """
    data = json.loads(request.body)

    location = write_files(data, 'run')
    path = os.environ['HOST_PATH'] + '/' + location[0]
    output = ([], '')

    language = data['info'][data['index']]['language']

    if language == 'Java':
        output = java_handler(data, path, location[1])
    elif language == 'Text':
        line1 = "You silly Billy, I Can't run Text files."
        line2 = "Try to run the tab with your Main method instead."
        output = ([line1, line2], -1)
    elif language == 'C++':
        output = cpp_handler(data, path, location[1])
    elif language == 'Python':
        command = 'python:2 python ' + data['info'][data['index']]['title']
        output = general_handler(path, location[1], command)
    elif language == 'Bash':
        command = 'bash:4.4 bash ' + data['info'][data['index']]['title']
        output = general_handler(path, location[1], command)
    elif language == 'Golang':
        output = go_handler(data, path, location[1])
    elif language == 'ObjectiveC':
        output = objective_c_handler(data, path, location[1])
    elif language == 'Perl':
        command = 'perl:5.20 perl ' + data['info'][data['index']]['title']
        output = general_handler(path, location[1], command)
    elif language == 'Ruby':
        command = 'ruby:2.1 ruby ' + data['info'][data['index']]['title']
        output = general_handler(path, location[1], command)
    elif language == 'Scala':
        output = scala_handler(data, path, location[1])
    elif language == 'Lisp':
        command = 'lisp clisp ' + data['info'][data['index']]['title']
        output = general_handler(path, location[1], command)

    ret = {'ret_val': output[1], 'output': output[0]}

    if output[1] != -1:
        ret.update({'stats': output[2]})

    os.system('rm -rf ' + location[0])
    return JsonResponse(ret)

def general_handler(path, unique_id, command):
    """
    This method depends on the correct command in order to use the correct image
    and exec command.
    """
    docker_run = 'docker run --rm --name ' + unique_id + ' -v ' + path +':/app -w /app ' + command
    result = run_docker_cont.delay(docker_run)

    stats, container_id = get_stats(unique_id)

    if stats == -1:
        docker_build = 'docker kill ' + container_id
        commands.getstatusoutput(docker_build)
        output = ["Hacker Alert AKA SlowPoke!!!",
        "Your program was killed because it was taking too long to finish.",
        "Watch out for infinite loops and don't be greedy.",
        "Other users want to have fun too."]
        clean_up(container_id, unique_id)
        return (output, -1)
    elif stats == -2:
        output = 'Failed to initiate.'
        return (output, -1)


    output = result.collect().next()[1]
    output = output.split('\n')

    if len(output)>50:
        return (['Output is to long.'], -1)

    new_output = []

    for i in output:
        if len(i)>100:
            new_output.append('Line is too long')
        else:
            new_output.append(i)

    clean_up(container_id, unique_id)

    return (output, container_id, stats)

def java_handler(data, path, unique_id):
    """
    Compile code first, deal with output accordingly.
    Run general_handler
    """

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app java:7 javac ' + data['info'][data['index']]['title']

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return (output.split('\n'), -1)

    split_title = data['info'][data['index']]['title'].split('.')
    split_title.pop(len(split_title)-1)
    command = 'java:7 java ' + '.'.join(split_title)

    return general_handler(path, unique_id, command)

def scala_handler(data, path, unique_id):
    """
    Compile scala code first, deal with output accordingly.
    Run general_handler
    """
    title = data['info'][data['index']]['title']

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app williamyeh/scala scalac ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return (output.split('\n'), -1)

    split_title = title.split('.')
    split_title.pop(len(split_title)-1)
    command = 'williamyeh/scala scala ' + '.'.join(split_title)

    return general_handler(path, unique_id, command)

def cpp_handler(data, path, unique_id):
    """
    Compile code first, deal with output accordingly.
    Run general_handler
    """

    language = data['info'][data['index']]['language']
    title = data['info'][data['index']]['title']

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app gcc:4.9 g++ -o cpp_app ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return (output.split('\n'), -1)

    command = 'gcc:4.9 ./cpp_app'

    return general_handler(path, unique_id, command)

def go_handler(data, path, unique_id):
    """
    Compile go code first, deal with output accordingly.
    Run general_handler
    """

    title = data['info'][data['index']]['title']

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app golang:1.6 go build -o golang_app -v ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return (output.split('\n'), -1)

    command = 'golang:1.6 ./golang_app'

    return general_handler(path, unique_id, command)

def objective_c_handler(data, path, unique_id):
    """
    Compile objective-c code first, deal with output accordingly.
    Run general_handler
    """

    title = data['info'][data['index']]['title']

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app nacyot/objectivec-gcc:apt gcc -o obj_c_app ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return (output.split('\n'), -1)

    command = 'nacyot/objectivec-gcc:apt ./obj_c_app'

    return general_handler(path, unique_id, command)

def clean_up(container_id, image_id):
    """clean up container and image"""
    docker_build = 'docker rm ' + container_id
    commands.getstatusoutput(docker_build)
    docker_build = 'docker rmi ' + image_id
    commands.getstatusoutput(docker_build)

def get_stats(unique_id):
    """Collect stats while container is running"""
    poll_time = 0.001
    running_time = 0
    command = 'docker ps --no-trunc | grep ' + unique_id
    while running_time <= 1:
        _, ids = commands.getstatusoutput(command)
        container_info = ids.split()
        if container_info != []:
            files = get_stats_location(container_info[0])
            return get_data(files), container_info[0]
        time.sleep(poll_time)
        running_time = running_time + poll_time
    return -2, -1

def get_data(files):
    """
    Keep reading while container is running (while files exist)
    """
    stats = [['time', 'cpu', 'core1', 'core2',
              'core3', 'core4', 'memory', 'disk_io']]

    poll_time = 0.01
    running_time = poll_time
    while os.path.exists(files[0]):
        data = []
        try:
            count = 1
            data.append(str(running_time))
            for fname in files:
                with open(fname) as stats_file:
                    if count == 2:
                        data = data + stats_file.read().rstrip('\n').split()
                    elif count == 4:
                        data.append(stats_file.readline().rstrip('\n').split()[1])
                    else:
                        data.append(stats_file.read().rstrip('\n'))
                count = count + 1
            time.sleep(poll_time)
        except IOError:
            pass
        else:
            stats.append(data)
            running_time = running_time + poll_time
            if str(running_time) == '10.0':
                return -1
    return stats

def get_stats_location(docker_id):
    """
    Stats for container cpu usage, individual core usage,
    and memory(Ram) usage and disk memory usage can be extracted from:
    /cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.usage,
    /cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.usage_percpu
    /cgroup/memory/docker/$CONTAINER_ID/memory.usage_in_bytes
    /cgroup/memory/docker/$CONTAINER_ID/memory.stat
    """
    location = '/cgroup/cpuacct/docker/'
    data_file = '/cpuacct.usage'
    cpu = location + docker_id + data_file

    location = '/cgroup/cpuacct/docker/'
    data_file = '/cpuacct.usage_percpu'
    core = location + docker_id + data_file

    location = '/cgroup/memory/docker/'
    data_file = '/memory.usage_in_bytes'
    memory = location + docker_id + data_file

    location = '/cgroup/memory/docker/'
    data_file = '/memory.stat'
    disk_io = location + docker_id + data_file

    return [cpu, core, memory, disk_io]

def write_files(data, mode):
    """
    Store user input files in some temp location, so they can be used inside
    a docker container.
    """
    unique_name = str(uuid.uuid4())
    unique_dir = 'running_dir/' + unique_name + '/'
    os.system('mkdir ' + unique_dir)

    if mode == 'static':
        file_name = unique_dir + data['info']['title']
        os.system('touch ' + file_name)
        writter = open(file_name, 'r+')
        writter.write(data['file'])
        writter.close()
    else:
        count = 0
        for entry in data['info']:
            file_name = unique_dir + entry['title']
            os.system('touch ' + file_name)
            writter = open(file_name, 'r+')
            writter.write(data['files'][count])
            writter.close()
            count = count + 1

    return (unique_dir, unique_name)
