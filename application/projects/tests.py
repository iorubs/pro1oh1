from django.test import TestCase
import unittest
from authentication.models import Account
from django.test import Client
from .views import *

from projects.models import Project, File

import os, shutil, json
from datetime import datetime
from django.http import JsonResponse

class ModelTestCase(TestCase):
    def setUp(self):
        self.test_user = Account.objects.create(
            email='test_user@model.ie',
            username='unit',
            first_name='test',
            last_name='user'
        )
        self.test_user.save()
        self.list_p = Project.objects.create(author=self.test_user, title='lp')
        self.list_p.save()
        self.update_p = Project.objects.create(author=self.test_user, title='up')
        self.update_p.save()
        self.update_f = File.objects.create(project=self.update_p, title='update_f', f_type='folder')
        self.update_f.save()
        self.delete_p = Project.objects.create(author=self.test_user, title='dp')
        self.delete_p.save()
        self.delete_f = File.objects.create(project=self.update_p, title='delete_f', f_type='file')
        self.delete_f.save()

    def test_create_project(self):
        """Create new project, check if project was added to DB"""
        test_project = Project.objects.create(author=self.test_user, title='pj')
        test_project.save()
        self.assertEqual(Project.objects.get(id=test_project.id).title, 'pj')

    def test_list_projects(self):
        """List user projects, verify with expected output"""
        queryset = Project.objects.select_related('author').all()
        queryset = queryset.filter(title=self.list_p.title)
        self.assertNotEqual(len(queryset), 0)

    def test_update_project(self):
        """Update project, check if DB was updated"""
        self.update_p.title = 'up-v2'
        self.update_p.save()
        queryset = Project.objects.select_related('author').all()
        queryset = queryset.filter(id=self.update_p.id)
        self.assertNotEqual(queryset, [])
        self.assertEqual(queryset[0].title, 'up-v2')

    def test_delete_project(self):
        """Delete project, check if it was removed from DB"""
        self.delete_p.delete()
        queryset = Project.objects.select_related('author').all()
        queryset = queryset.filter(title=self.delete_p.title)
        self.assertEqual(len(queryset), 0)

    def test_create_file(self):
        """Create new file/folder, check if file was added to DB"""
        test_file = File.objects.create(project=self.update_p, title='create_file', f_type='file')
        test_file.save()
        self.assertEqual(File.objects.get(id=test_file.id).title, 'create_file')

    def test_create_sub_file(self):
        """
        Create new subfile, check if subfile was added to DB
        A subfile is a file with another file as a foreign key(folder)
        """
        test_sub_file = File.objects.create(project=self.update_p, folder=self.update_f, title='create_sub_file', f_type='file')
        test_sub_file.save()
        queryset = File.objects.select_related('project').all()
        queryset = queryset.filter(folder__id=self.update_f.id)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].title, 'create_sub_file')

    def test_update_file(self):
        """Update file/folder, check if DB was updated"""
        self.update_f.title = 'update_f-v2'
        self.update_f.save()
        self.assertEqual(File.objects.get(id=self.update_f.id).title, 'update_f-v2')

    def test_delete_file(self):
        """Delete file/folder, check if it was removed from DB"""
        self.delete_f.delete()
        queryset = File.objects.select_related('project').all()
        queryset = queryset.filter(title=self.delete_f.title)
        self.assertEqual(len(queryset), 0)

class HTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post('/api/v1/accounts/',{
            'username': 'http',
            'password': 'unit',
            'email': 'http@unit.ie',
            'first_name': 'un',
            'last_name': 'it'
        })
        self.client.login(username='http', password='unit')

        title = json.dumps({'title': 'list_test'})
        self.client.post('/api/v1/projects/', title, content_type="application/json")

        title = json.dumps({'title': 'update_test'})
        response = self.client.post('/api/v1/projects/', title, content_type="application/json")
        data = json.loads(response.content)
        self.update_id = data['id']
        list_file = json.dumps({'title': 'list_test', 'f_type': 'py', 'content': 'print "hello world"'})
        response = self.client.post('/api/v1/files/', list_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')

        update_file = json.dumps({'title': 'update_test', 'f_type': 'py', 'content': 'print "hello world"'})
        response = self.client.post('/api/v1/files/', update_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.update_file_id = data['id']

        title = json.dumps({'title': 'delete_test'})
        response = self.client.post('/api/v1/projects/', title, content_type="application/json")
        data = json.loads(response.content)
        self.delete_id = data['id']

        delete_file = json.dumps({'title': 'delete_file', 'f_type': 'py', 'content': 'print "hello world"'})
        response = self.client.post('/api/v1/files/', delete_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.delete_file_id = data['id']

        python_file = json.dumps({'title': 'test', 'f_type': 'py', 'content': 'print "bar"'})
        response = self.client.post('/api/v1/files/', python_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.python_file_id = data['id']

        java_file = json.dumps({'title': 'Test.java', 'f_type': 'java', 'content': 'public class Test{public static void main (String[] args) {System.out.printf("bar");}}'})
        response = self.client.post('/api/v1/files/', java_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.java_file_id = data['id']

        cpp_file = json.dumps({'title': 'test.cpp', 'f_type': 'cpp', 'content': '#include <iostream>\nint main() {std::cout << "bar" << std::endl;return 0;}'})
        response = self.client.post('/api/v1/files/', cpp_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.cpp_file_id = data['id']

        perl_file = json.dumps({'title': 'test.prl', 'f_type': 'prl', 'content': '#!/usr/bin/perl\nuse strict;\nuse warnings;\nprint "bar";'})
        response = self.client.post('/api/v1/files/', perl_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.perl_file_id = data['id']

        bash_file = json.dumps({'title': 'test.sh', 'f_type': 'sh', 'content': "#!/usr/bin/bash\necho 'bar'"})
        response = self.client.post('/api/v1/files/', bash_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.bash_file_id = data['id']

        golang_file = json.dumps({'title': 'test.go', 'f_type': 'go', 'content': 'package main\nimport "fmt"\nfunc main() {fmt.Println("bar")}'})
        response = self.client.post('/api/v1/files/', golang_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.golang_file_id = data['id']

        objectivec_file = json.dumps({'title': 'test.m', 'f_type': 'm', 'content': '#import <stdio.h>\nint main(){printf("bar");return 0;}'})
        response = self.client.post('/api/v1/files/', objectivec_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.objectivec_file_id = data['id']

        ruby_file = json.dumps({'title': 'test.rb', 'f_type': 'rb', 'content': "puts 'bar'"})
        response = self.client.post('/api/v1/files/', ruby_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.ruby_file_id = data['id']

        scala_file = json.dumps({'title': 'test.scala', 'f_type': 'scala', 'content': 'object test {def main(args: Array[String]): Unit = {println("bar")}}'})
        response = self.client.post('/api/v1/files/', scala_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.scala_file_id = data['id']

        lisp_file = json.dumps({'title': 'test.lisp', 'f_type': 'lisp', 'content': '(print "bar")'})
        response = self.client.post('/api/v1/files/', lisp_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        data = json.loads(response.content)
        self.lisp_file_id = data['id']


    def test_create_project_http(self):
        """Create project using the API, check response"""
        title = json.dumps({'title': 'create_test'})
        response = self.client.post('/api/v1/projects/', title, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'create_test')
        self.assertEqual(data['author']['email'], 'http@unit.ie')

    def test_list_projects_http(self):
        """List user projects using the API, check response"""
        response = self.client.get('/api/v1/accounts/http/projects/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = False
        for p in data:
            if p['title'] == 'list_test':
                found = True

        self.assertTrue(found)

    def test_update_project_http(self):
        """Update project using the API, check response"""
        project = json.dumps({'title': 'update_test_v2'})
        response = self.client.put('/api/v1/projects/' +  str(self.update_id) + '/', project, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'update_test_v2')

    def test_delete_project_http(self):
        """Delete project using the API, check response"""
        response = self.client.delete('/api/v1/projects/' + str(self.delete_id) + '/', content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_create_file_http(self):
        """Create file/folder using the API, check response"""
        create_file = json.dumps({'title': 'create_test', 'f_type': 'file', 'content': 'test'})
        response = self.client.post('/api/v1/files/', create_file, content_type="application/json",
                                    HTTP_PROJECT=self.update_id, HTTP_FOLDER='None')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'create_test')
        self.assertEqual(data['folder'], None)
        self.assertEqual(data['project']['title'], 'update_test')

    def test_list_files_http(self):
        """List project files/folders using the API, check response"""
        response = self.client.get('/api/v1/projects/' + str(self.update_id) + '/files/', content_type="application/json", HTTP_FOLDER='None')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        tmp_file = None
        for f in data:
            if f['title'] == 'list_test':
                tmp_file = f

        self.assertNotEqual(tmp_file, None)

    def test_update_file_http(self):
        """Update file/folder using the API, check response"""
        update_file = json.dumps({'title': 'update_test-v2', 'f_type': 'py', 'content': 'new'})
        response = self.client.put('/api/v1/files/' +  str(self.update_file_id) + '/', update_file, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'update_test-v2')
        self.assertEqual(data['content'], 'new')

    def test_delete_file_http(self):
        """Delete file/folder using the API, check response"""
        response = self.client.delete('/api/v1/files/' + str(self.delete_file_id) + '/', content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_project_static_run_python_http(self):
        """Python project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.python_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'C:  1, 0: Missing module docstring (missing-docstring)'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_java_http(self):
        """Java project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.java_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Starting audit...'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_cpp_http(self):
        """C++ project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.cpp_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Done processing test.cpp'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_perl_http(self):
        """Perl project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.perl_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'test.prl source OK'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_bash_http(self):
        """Bash project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.bash_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'All good.'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_golang_http(self):
        """Golang project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.golang_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Coding correctness.'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_objectivec_http(self):
        """ObjectiveC project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.objectivec_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'OCLint Report'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_ruby_http(self):
        """Ruby project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.ruby_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'All good.'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_static_run_scala_http(self):
        """Scala project static analyses - Send request and check output"""
        data = json.dumps({'id' : self.scala_file_id})
        response = self.client.post('/api/v1/project/staticrun/', data, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Processed 1 file(s)'
        self.assertEqual(expected_line in data['output'], True)

    def test_project_run_python_http(self):
        """Python project run - Send run request and check output"""
        data = json.dumps({'id' : self.python_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_java_http(self):
        """Java project run - Send run request and check output"""
        data = json.dumps({'id' : self.java_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_cpp_http(self):
        """C++ project run - Send run request and check output"""
        data = json.dumps({'id' : self.cpp_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_perl_http(self):
        """Perl project run - Send run request and check output"""
        data = json.dumps({'id' : self.perl_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_bash_http(self):
        """Bash project run - Send run request and check output"""
        data = json.dumps({'id' : self.bash_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_golang_http(self):
        """Golang project run - Send run request and check output"""
        data = json.dumps({'id' : self.golang_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_objectivec_http(self):
        """ObjectiveC project run - Send run request and check output"""
        data = json.dumps({'id' : self.objectivec_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_ruby_http(self):
        """Ruby project run - Send run request and check output"""
        data = json.dumps({'id' : self.ruby_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_scala_http(self):
        """Scala project run - Send run request and check output"""
        data = json.dumps({'id' : self.scala_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'][0], 'bar')

    def test_project_run_lisp_http(self):
        """Lisp project run - Send run request and check output"""
        data = json.dumps({'id' : self.lisp_file_id, 'p_start': 'start', 'p_end': 'end'})
        response = self.client.post('/api/v1/project/run/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(str(data['output'][1]), '"bar" ')

    def test_clone_http(self):
        """Clone project, check status message, return code
        and if the project was inserted into the DB"""
        git_command = 'git clone https://github.com/iorubs/pro1oh1_git_comp.git'
        data = json.dumps({'clone_command': git_command})

        response = self.client.post('/api/v1/project/git-clone/', data, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'Success')

        queryset = Project.objects.select_related('author').all()
        queryset = queryset.filter(title='pro1oh1_git_comp')
        self.assertNotEqual(len(queryset), 0)
        queryset[0].delete()

class FuncTestCase(TestCase):
    def setUp(self):
        os.mkdir('unit_tests')
        os.mkdir('unit_tests/run')
        os.mkdir('unit_tests/static')
        os.mkdir('unit_tests/run/breakpoints')

        self.test_user = Account.objects.create(
            email='func_test_user@model.ie',
            username='func_unit',
            first_name='test',
            last_name='user'
        )
        self.test_user.save()
        self.test_proj = Project.objects.create(author=self.test_user, title='test_proj')
        self.test_proj.save()
        self.test_file = File.objects.create(project=self.test_proj, title='test_func_file.py', f_type='py', content='print "hello world"')
        self.test_file.save()

    def test_write_static_files(self):
        """Check if the static files were created in the correct place"""
        path = 'unit_tests/static/'
        create_static_files(path, self.test_file)
        self.assertEqual(os.path.exists(path), True)
        self.assertEqual(os.path.exists(path+'test_func_file.py'), True)


    def test_write_run_files(self):
        """Check if the run files were created in the correct place"""
        path = 'unit_tests/run/'
        queryset = File.objects.select_related('project').all()
        queryset = queryset.filter(project__id=self.test_file.project.id, folder=None)
        create_code_run_files(queryset, path)
        self.assertEqual(os.path.exists(path), True)
        self.assertEqual(os.path.exists(path+'test_func_file.py'), True)

    def test_break_points(self):
        """Check if the break points/imports were inserted in the correct place"""
        path = 'unit_tests/run/breakpoints/'
        queryset = File.objects.select_related('project').all()
        queryset = queryset.filter(project__id=self.test_file.project.id, folder=None)
        create_code_run_files(queryset, path)
        self.assertEqual(os.path.exists(path), True)
        self.assertEqual(os.path.exists(path+'test_func_file.py'), True)

        set_break_points('0', '0', self.test_file, path)
        file_name = path + 'test_func_file.py'
        f = open(file_name, "r")
        contents = f.readlines()
        f.close()
        import_str = 'from datetime import datetime\n'
        start_bp = "print 'pro1oh1_end_break_point.' + '.'.join(str(datetime.time(datetime.now())).split(':'))\n"
        end_bp = "print 'pro1oh1_start_break_point.' + '.'.join(str(datetime.time(datetime.now())).split(':'))\n"

        self.assertEqual(contents[0], import_str)
        self.assertEqual(contents[1], start_bp)
        self.assertEqual(contents[2], end_bp)

    def test_docker_stats(self):
        """Check if the correct number of files was returned"""
        files = get_stats_location('ID')
        self.assertEqual(len(files), 4)

    def tearDown(self):
        shutil.rmtree('unit_tests', ignore_errors=True)
