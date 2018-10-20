from django.test import TestCase
import unittest
from django.test import Client
from .views import *

import os, shutil, json
from django.http import JsonResponse

class FuncTestCase(TestCase):
    def setUp(self):
        os.mkdir('unit_tests')

    def test_docker_stats(self):
        """Check if the correct number of files was returned"""
        files = get_stats_location('ID')
        self.assertEqual(len(files), 4)

    def tearDown(self):
        shutil.rmtree('unit_tests', ignore_errors=True)

class HTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_quick_static_run_python_http(self):
        """Normal static analyses of python code - send request and check output"""
        foo = "print 'bar'"
        fileInfo = {'title': 'test', 'language': 'Python'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = '************* Module test'
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_java_http(self):
        """Normal static analyses of java code - send request and check output"""
        foo = 'public class Test{public static void main (String[] args) {System.out.printf("bar");}}'
        fileInfo = {'title': 'Test.java', 'language': 'Java'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Starting audit...'
        self.assertEqual(len(data['output']), 10)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_cpp_http(self):
        """Normal static analyses of cpp code - send request and check output"""
        foo = '#include <iostream>\nint main() {std::cout << "bar" << std::endl;return 0;}'
        fileInfo = {'title': 'test.cpp', 'language': 'C++'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Done processing test.cpp'
        self.assertEqual(len(data['output']), 5)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_perl_http(self):
        """Normal static analyses of perl code - send request and check output"""
        foo = '#!/usr/bin/perl\nuse strict;\nuse warnings;\nprint "bar";'
        fileInfo = {'title': 'test.prl', 'language': 'Perl'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'test.prl source OK'
        self.assertEqual(len(data['output']), 1)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_bash_http(self):
        """Normal static analyses of bash code - send request and check output"""
        foo = "#!/usr/bin/bash\necho 'bar'"
        fileInfo = {'title': 'test.sh', 'language': 'Bash'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'All good.'
        self.assertEqual(len(data['output']), 1)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_golang_http(self):
        """Normal static analyses of golang code - send request and check output"""
        foo = 'package main\nimport "fmt"\nfunc main() {fmt.Println("bar")}'
        fileInfo = {'title': 'test.go', 'language': 'Golang'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Coding correctness.'
        self.assertEqual(len(data['output']), 5)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_objectivec_http(self):
        """Normal static analyses of objective-c code - send request and check output"""
        foo = '#import <stdio.h>\nint main(){printf("bar");return 0;}'
        fileInfo = {'title': 'test.m', 'language': 'ObjectiveC'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'OCLint Report'
        self.assertEqual(len(data['output']), 8)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_ruby_http(self):
        """Normal static analyses of ruby code - send request and check output"""
        foo = "puts 'bar'"
        fileInfo = {'title': 'test.rb', 'language': 'Ruby'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'All good.'
        self.assertEqual(len(data['output']), 1)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_static_run_scala_http(self):
        """Normal static analyses of scala code - send request and check output"""
        foo = '(print "bar")'
        fileInfo = {'title': 'test.scala', 'language': 'Scala'}
        jvar = json.dumps({'file': foo, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/staticrun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        expected_line = 'Processed 1 file(s)'
        self.assertEqual(len(data['output']), 5)
        self.assertEqual(expected_line in data['output'], True)

    def test_quick_run_python_http(self):
        """Normal quick run of python code - Send run request and check output"""
        files = ["print 'bar'"]
        fileInfo = [{'title': 'test.py', 'language': 'Python'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_java_http(self):
        """Normal quick run of java code - Send run request and check output"""
        files = ['public class Test{public static void main (String[] args) {System.out.printf("bar");}}']
        fileInfo = [{'title': 'Test.java', 'language': 'Java'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_cpp_http(self):
        """Normal quick run of c++ code - Send run request and check output"""
        files = ['#include <iostream>\nint main() {std::cout << "bar" << std::endl;return 0;}']
        fileInfo = [{'title': 'test.cpp', 'language': 'C++'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_perl_http(self):
        """Normal quick run of perl code - Send run request and check output"""
        files = ['#!/usr/bin/perl\nuse strict;\nuse warnings;\nprint "bar";']
        fileInfo = [{'title': 'test.prl', 'language': 'Perl'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_bash_http(self):
        """Normal quick run of bash code - Send run request and check output"""
        files = ["#!/usr/bin/bash\necho 'bar'"]
        fileInfo = [{'title': 'test.sh', 'language': 'Bash'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_golang_http(self):
        """Normal quick run of golang code - Send run request and check output"""
        files = ['package main\nimport "fmt"\nfunc main() {fmt.Println("bar")}']
        fileInfo = [{'title': 'test.go', 'language': 'Golang'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_objectivec_http(self):
        """Normal quick run of objective-c code - Send run request and check output"""
        files = ['#import <stdio.h>\nint main(){printf("bar");return 0;}']
        fileInfo = [{'title': 'test.m', 'language': 'ObjectiveC'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_ruby_http(self):
        """Normal quick run of ruby code - Send run request and check output"""
        files = ["puts 'bar'"]
        fileInfo = [{'title': 'test.rb', 'language': 'Ruby'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_scala_http(self):
        """Normal quick run of scala code - Send run request and check output"""
        files = ['object test {def main(args: Array[String]): Unit = {println("bar")}}']
        fileInfo = [{'title': 'test.scala', 'language': 'Scala'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(data['output'], ['bar'])

    def test_quick_run_lisp_http(self):
        """Normal quick run of lisp code - Send run request and check output"""
        files = ['(print "bar")']
        fileInfo = [{'title': 'test.lisp', 'language': 'Lisp'}]
        jvar = json.dumps({'files': files, 'index': 0, 'info': fileInfo})
        response = self.client.post('/api/v1/quick-run/singlerun/', jvar, content_type="application/json")
        data = json.loads(response.content)
        self.assertEqual(str(data['output'][1]), '"bar" ')
