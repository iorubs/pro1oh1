from rest_framework import permissions, viewsets
from rest_framework.response import Response

from projects.models import Project, File
from projects.permissions import IsAuthorOfProject, IsAuthorOfFile
from projects.serializers import ProjectSerializer, FileSerializer

from django.http import JsonResponse
import json
import os
import uuid
import commands
import time
from datetime import datetime

from projects.tasks import run_docker_cont

def cloneGitProjectView(request):
    """
    Receive input in JSON format, decode it,
    clone github project and add it to the user projects
    """
    data = json.loads(request.body)
    ret = {}

    location = running_dir()
    clone_command = 'cd ' + location[0] + ' && ' + data['git_clone']
    status, output = commands.getstatusoutput(clone_command)

    if status == 0:
        traversePojectFolder(location[0], request.user, data['git_enc'])
        ret = {'status': 'Success'}
    else:
        ret = {'status': 'Fail', 'error': output}

    os.system('rm -rf ' + location[0])
    return JsonResponse(ret)

def traversePojectFolder(location, author, clone_command):
    """Create Project and visit all children"""
    supported_lang = ['java', 'cpp', 'py']
    contents = os.listdir(location)
    loc = location + '/' + contents[0]
    project = Project(author=author, title=contents[0], p_type='git', clone_command=clone_command)
    project.save()
    traverseSubFolder(loc, project, None, supported_lang)

def traverseSubFolder(location, project, parent, supported_lang):
    """Visit all sub files/folders"""
    contents = os.listdir(location)

    for c in contents:
        file_path = location + '/' + c
        if os.path.isfile(file_path):
            with open(file_path) as f:
                content = f.readlines()

            content = ''.join(content)

            test = c.split('.')
            if test[len(test)-1] in supported_lang:
                File(project=project, folder=parent, title=c, f_type=test[len(test)-1], content=content).save()
            else:
                File(project=project, folder=parent, title=c, f_type='txt', content=content).save()
        else:
            if c != '.git':
                folder = File(project=project, folder=parent, title=c, f_type='folder')
                folder.save()
                traverseSubFolder(file_path, project, folder, supported_lang)

def pushGitProjectView(request):
    """
    Receive input in JSON format, decode it,
    fetch project, commit, push and remobe from DB
    """
    data = json.loads(request.body)
    ret = {}
    location = running_dir()

    project = Project.objects.get(id=data['project'])

    clone_command = 'cd ' + location[0] + ' && ' + project.clone_command;
    status, output = commands.getstatusoutput(clone_command)

    if status == 0:
        fetchAndWriteGitFiles(project.id, (location[0]+project.title+'/'))
    else:
        os.system('rm -rf ' + location[0])
        return JsonResponse({'status': 'Fail', 'error': output})

    commit_command = 'cd ' + location[0] + project.title + ' && git add --all && git commit -m "' + data['message'] + '"'
    status, output = commands.getstatusoutput(commit_command)

    if status != 0:
        os.system('rm -rf ' + location[0])
        return JsonResponse({'status': 'Fail', 'error': output})

    push_command = 'cd ' + location[0] + project.title + ' && git push'
    status, output = commands.getstatusoutput(push_command)

    if status == 0:
        ret = {'status': 'Success'}
    else:
        ret = {'status': 'Fail', 'error': output}

    os.system('rm -rf ' + location[0])
    return JsonResponse(ret)

def fetchAndWriteGitFiles(project_id, location):
    """Fetch list of file in the projects root level and call write method"""
    queryset = File.objects.select_related('project').all()
    queryset = queryset.filter(project__id=project_id, folder=None)
    over_write_git_files(queryset, location)

def over_write_git_files(queryset, path):
    """Over write all files/folders and sub files/folders."""
    for item in queryset:
        title = path + item.title
        if item.f_type == 'folder':
            if os.path.exists(title) == False:
                os.system('mkdir ' + title)
            new_set = File.objects.select_related('project').all()
            new_set = new_set.filter(folder__id=item.id)
            over_write_git_files(new_set, (title + '/'))
        else:
            f = open(title,'w')
            f.write(item.content)
            f.close()

def projectStaticView(request):
    """
    Receive input in JSON format,
    decode it, call the correct handler method,
    return static results
    """
    data = json.loads(request.body)
    main_file = File.objects.get(id=data['id'])

    location = running_dir()
    create_static_files(location[0], main_file)

    path = os.environ['HOST_PATH'] + '/' + location[0]
    ret = static_run(location[1], path, main_file)
    os.system('rm -rf ' + location[0])
    return JsonResponse(ret)

def static_run(name, path, main_file):
    status = 0
    output = []
    command = 'docker run --rm -v ' + path + ':/app -w /app static-tools '

    if main_file.f_type == 'java':
        command = command + 'java -jar /usr/src/app/checkstyle-6.13-all.jar -c /usr/src/app/google_std.xml '
        docker_run = command + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        if status != 0:
            new_output = []
            error = 'Caused by: /usr/src/app'
            for line in output:
                if error in line:
                    new_output.append(line)
            output = new_output
    elif main_file.f_type == 'py':
        docker_run = command + 'pylint --reports=n ' + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        output.pop(0)
    elif main_file.f_type == 'cpp':
        docker_run = command + 'cpplint ' + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    elif main_file.f_type  == 'go':
        go_vet = command + 'go vet ' + main_file.title
        status, output = commands.getstatusoutput(go_vet)
        output_vet = output.split('\n')

        if(output_vet[0] == '' and len(output_vet) == 1):
            output_vet = ['All good.']

        go_lint = command + 'golint ' + main_file.title
        status, output = commands.getstatusoutput(go_lint)
        output_lint = output.split('\n')
        if(output_lint[0] == '' and len(output_lint) == 1):
            output_lint = ['All good.']

        output = ['Coding correctness.'] + output_vet \
                + ['---------------------------'] \
                + ['Coding style.'] + output_lint
    elif main_file.f_type == 'm':
        docker_run = command + 'oclint ' + main_file.title + ' -- -c'
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    elif main_file.f_type == 'sh':
        docker_run = command + '/root/.cabal/bin/shellcheck ' + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        if(output[0] == '' and len(output) == 1):
            output = ['All good.']
    elif main_file.f_type == 'prl':
        docker_run = command + 'perlcritic -3 ' + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    elif main_file.f_type == 'rb':
        docker_run = command + 'ruby-lint ' + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
        if(output[0] == '' and len(output) == 1):
            output = ['All good.']
    elif main_file.f_type == 'scala':
        command = command + 'java -jar /usr/src/app/scalastyle_2.10-0.8.0-batch.jar --config /usr/src/app/scalastyle_config.xml '
        docker_run = command + main_file.title
        status, output = commands.getstatusoutput(docker_run)
        output = output.split('\n')
    else:
        output = main_file.f_type + " File type not supported"

    return {'output': output}

def create_static_files(location, main_file):
    """
    Write the file being analysed and the Dockerfile used for
    running it, in the apropiate container.
    """
    title = location + main_file.title
    f = open(title,'w')
    f.write(main_file.content)
    f.close()

def projectRunView(request):
    """
    Receive input in JSON format,
    decode it, call the correct handler method,
    return results
    """
    data = json.loads(request.body)
    main_file = File.objects.get(id=data['id'])

    location = running_dir()
    queryset = File.objects.select_related('project').all()

    if main_file.folder is None:
        queryset = queryset.filter(project__id=main_file.project.id, folder=None)
    else:
        queryset = queryset.filter(folder__id=main_file.folder.id)

    create_code_run_files(queryset, location[0])

    if data['p_start'] != 'start' or data['p_end'] != 'end':
        set_break_points(data['p_start'], data['p_end'], main_file, location[0])

    start_time = ['0']
    output = {}

    path = os.environ['HOST_PATH'] + '/' + location[0]

    if main_file.f_type == 'java':
        output = java_handler(main_file.title, path, location[1], start_time)
    elif main_file.f_type == 'cpp':
        output = cpp_handler(main_file, path, location[1], start_time)
    elif main_file.f_type == 'py':
        command = 'python:2 python ' + main_file.title
        output = general_handler(path, location[1], start_time, command)
    elif main_file.f_type == 'sh':
        command = 'bash:4.4 bash ' + main_file.title
        output = general_handler(path, location[1], start_time, command)
    elif main_file.f_type == 'go':
        output = go_handler(main_file.title, path, location[1], start_time)
    elif main_file.f_type == 'm':
        output = objective_c_handler(main_file.title, path, location[1], start_time)
    elif main_file.f_type == 'prl':
        command = 'perl:5.20 perl ' + main_file.title
        output = general_handler(path, location[1], start_time, command)
    elif main_file.f_type == 'rb':
        command = 'ruby:2.1 ruby ' + main_file.title
        output = general_handler(path, location[1], start_time, command)
    elif main_file.f_type == 'scala':
        output = scala_handler(main_file.title, path, location[1], start_time)
    elif main_file.f_type == 'lisp':
        command = 'lisp clisp ' + main_file.title
        output = general_handler(path, location[1], start_time, command)
    elif main_file.f_type == 'txt':
        line1 = "You silly Billy, I Can't run Text files."
        output = {'output': [line1]}
    else:
        line1 = main_file.f_type + " File type not supported"
        output = {'output': [line1]}

    start_time = start_time[0].split('.')
    start_time = [int(i) for i in start_time]

    break_points = ['0', '0']

    if data['p_start'] != 'start' or data['p_end'] != 'end':
        find_break_points(output, break_points)
        if break_points[0] != '0' or break_points[1] != '0':
            output['points'] = calculate_time_diff(start_time, break_points, output['stats'])

    os.system('rm -rf ' + location[0])

    return JsonResponse(output)

def calculate_time_diff(start_time, break_points, stats):
    """
    Calculate when the points were executed.
    """
    start_index = 1
    end_index = len(stats)-1

    p = start_time[3] + ((start_time[2] + ((start_time[1] + (start_time[0] * 60)) * 60)) * 1000000)

    if break_points[0] != '0':
        if break_points[0][0] < start_time[0]:
            break_points[0][0] = break_points[0][0]+24

        sp = break_points[0][3] + ((break_points[0][2] + ((break_points[0][1] + (break_points[0][0] * 60)) * 60)) * 1000000)
        start_index = int(round((sp - p)/10000.0))

    if break_points[1] != '0':
        if break_points[1][0] < start_time[0]:
            break_points[1][0] = break_points[1][0]+24

        ep = break_points[1][3] + ((break_points[1][2] + ((break_points[1][1] + (break_points[1][0] * 60)) * 60)) * 1000000)
        end_index = int(round((ep - p)/10000.0))

    return [start_index, end_index]

def find_break_points(output, break_points):
    """
    Find the break points in the output,
    in order to calculate when they were executed.
    """
    index = 0
    start = -1
    end = -1

    for line in output['output']:
        split_line = line.split('.')
        if split_line[0] == 'pro1oh1_start_break_point':
            break_points[0] = split_line[1:]
            break_points[0] = [int(i) for i in break_points[0]]
            start = index
        elif split_line[0] == 'pro1oh1_end_break_point':
            break_points[1] = split_line[1:]
            break_points[1] = [int(i) for i in break_points[1]]
            end = index
        index = index + 1

    if start != -1:
        output['output'].pop(start)
        end = end - 1

    if(end > -1):
        output['output'].pop(end)

def set_break_points(start, end, main_file, location):
    """
    Insert break points into the file,
    in order to extract specific data.
    """
    #read file lines and store it in contents
    file_name = location + main_file.title
    f = open(file_name, "r")
    contents = f.readlines()
    f.close()

    if end != 'end':
        insert_end_b_points(contents, int(end)-1, main_file)

    if start != 'start':
        insert_start_b_points(contents, int(start)-1, main_file)

    insert_point_imports(contents, main_file)

    #re-write file lines and insert break points
    f = open(file_name, "w")
    contents = "\n".join(contents)
    f.write(contents)
    f.close()

def insert_point_imports(contents, main_file):
    """Insert specific language imports into into user code"""
    if main_file.f_type == 'py':
        contents.insert(0, 'from datetime import datetime')
    elif main_file.f_type == 'java':
        contents.insert(0, 'import java.text.SimpleDateFormat; import java.util.Date;')

def insert_start_b_points(contents, start, main_file):
    """Insert the start breaking point into user code"""
    if main_file.f_type == 'py':
        contents.insert(start, "print 'pro1oh1_start_break_point.' + '.'.join(str(datetime.time(datetime.now())).split(':'))")
    elif main_file.f_type == 'java':
        contents.insert(start, 'System.out.printf("pro1oh1_start_break_point.%s%n", new SimpleDateFormat("HH.mm.ss.SSS000").format(new Date()));')

def insert_end_b_points(contents, end, main_file):
    """Insert the end breaking point into user code"""
    if main_file.f_type == 'py':
        contents.insert(end, "print 'pro1oh1_end_break_point.' + '.'.join(str(datetime.time(datetime.now())).split(':'))")
    elif main_file.f_type == 'java':
        contents.insert(end, 'System.out.printf("pro1oh1_end_break_point.%s%n", new SimpleDateFormat("HH.mm.ss.SSS000").format(new Date()));')

def general_handler(path, unique_id, start_time, command):
    """
    This method depends on the correct command in order to use the correct image
    and run command.
    """

    docker_run = 'docker run --rm --name ' + unique_id + ' -v ' + path +':/app -w /app ' + command
    result = run_docker_cont.delay(docker_run)
    stats, container_id = get_stats(unique_id, start_time)

    if stats == -1:
        docker_build = 'docker kill ' + container_id
        commands.getstatusoutput(docker_build)
        output = ["Hacker Alert AKA SlowPoke!!!",
        "Your program was killed because it was taking too long to finish.",
        "Watch out for infinite loops and don't be greedy.",
        "Other users want to have fun too."]
        clean_up(container_id, unique_id)
        return {'output': output, 'stats': ''}
    elif stats == -2:
        output = ['Failed to initiate.']
        return {'output': output, 'stats': ''}

    out = result.collect().next()[1]
    output = out.split('\n')

    if len(output)>50:
        return {'output': ['Output is to long.'], 'stats': stats}

    new_output = []

    for i in output:
        if len(i)>100:
            new_output.append('Line is too long')
        else:
            new_output.append(i)

    clean_up(container_id, unique_id)

    return {'output': new_output, 'stats': stats}

def clean_up(container_id, image_id):
    """clean up container and image"""
    docker_build = 'docker rm ' + container_id
    commands.getstatusoutput(docker_build)
    docker_build = 'docker rmi ' + image_id
    commands.getstatusoutput(docker_build)

def get_stats(unique_id, start_time):
    """Collect stats while container is running"""
    poll_time = 0.001
    running_time = 0
    command = 'docker ps --no-trunc | grep ' + unique_id
    while running_time <= 1:
        _, ids = commands.getstatusoutput(command)
        container_info = ids.split()
        if container_info != []:
            files = get_stats_location(container_info[0])
            start_time[0] = '.'.join(str(datetime.time(datetime.now())).split(':'))
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

def java_handler(title, path, unique_id, start_time):
    """
    Compile code first, deal with output accordingly.
    Run general_handler
    """

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app java:7 javac ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return {'output': output.split('\n')}

    split_title = title.split('.')
    split_title.pop(len(split_title)-1)
    command = 'java:7 java ' + '.'.join(split_title)

    return general_handler(path, unique_id, start_time, command)

def scala_handler(title, path, unique_id, start_time):
    """
    Compile scala code first, deal with output accordingly.
    Run general_handler
    """

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app williamyeh/scala scalac ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return {'output': output.split('\n')}

    split_title = title.split('.')
    split_title.pop(len(split_title)-1)
    command = 'williamyeh/scala scala ' + '.'.join(split_title)

    return general_handler(path, unique_id, start_time, command)

def cpp_handler(main_file, path, unique_id, start_time):
    """
    Compile code first, deal with output accordingly.
    Run general_handler
    """

    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app gcc:4.9 g++ -o cpp_app ' + main_file.title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return {'output': output.split('\n')}

    command = 'gcc:4.9 ./cpp_app'
    return general_handler(path, unique_id, start_time, command)

def go_handler(title, path, unique_id, start_time):
    """
    Compile go code first, deal with output accordingly.
    Run general_handler
    """
    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app golang:1.6 go build -o golang_app -v ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return {'output': output.split('\n')}

    command = 'golang:1.6 ./golang_app'

    return general_handler(path, unique_id, start_time, command)

def objective_c_handler(title, path, unique_id, start_time):
    """
    Compile objective-c code first, deal with output accordingly.
    Run general_handler
    """
    docker_compile = 'docker run --rm -v ' + path \
    + ':/app -w /app nacyot/objectivec-gcc:apt gcc -o obj_c_app ' + title

    status, output = commands.getstatusoutput(docker_compile)
    if status != 0:
        return {'output': output.split('\n')}

    command = 'nacyot/objectivec-gcc:apt ./obj_c_app'

    return general_handler(path, unique_id, start_time, command)

def create_code_run_files(queryset, path):
    """Write all files/folders and sub files/folders."""
    for item in queryset:
        title = path + item.title
        if item.f_type == 'folder':
            os.system('mkdir ' + title)
            new_set = File.objects.select_related('project').all()
            new_set = new_set.filter(folder__id=item.id)
            create_code_run_files(new_set, (title + '/'))
        else:
            f = open(title,'w')
            f.write(item.content)
            f.close()

def running_dir():
    """
    Store user input into files, so they can be run inside
    a docker container.
    """
    unique_name = str(uuid.uuid4())
    unique_dir = 'running_dir/' + unique_name + '/'
    os.system('mkdir ' + unique_dir)

    return (unique_dir, unique_name)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('author').all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAuthorOfProject(),)

    def list(self, request, account_username=None):
        queryset = self.queryset.filter(author__username=account_username)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)
        return super(ProjectViewSet, self).perform_create(serializer)

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.select_related('project').all()
    serializer_class = FileSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAuthorOfFile(),)

    def list(self, request, project_pk=None):
        folder_id = self.request.META['HTTP_FOLDER']
        if folder_id == 'None':
            queryset = self.queryset.filter(project__id=project_pk, folder=None)
        else:
            queryset = self.queryset.filter(project__id=project_pk, folder__id=folder_id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        pro_id = self.request.META['HTTP_PROJECT']
        folder_id = self.request.META['HTTP_FOLDER']

        if folder_id == 'None':
            instance = serializer.save(project=Project.objects.get(id=pro_id), folder=None)
        else:
            instance = serializer.save(project=Project.objects.get(id=pro_id), folder=File.objects.get(id=folder_id))
        return super(FileViewSet, self).perform_create(serializer)
