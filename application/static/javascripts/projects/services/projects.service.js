(function () {
  'use strict';

  angular
    .module('pro1oh1.projects.services')
    .factory('Projects', Projects);

  Projects.$inject = ['$http'];

  function Projects($http) {
    var Projects = {
      create: create,
      remove: remove,
      get: get,
      update: update,
      create_file: create_file,
      remove_file: remove_file,
      get_files: get_files,
      update_file: update_file,
      staticRun: staticRun,
      run: run,
      clone: clone,
      push: push
    };

    return Projects;

    function create(title) {
      return $http.post('/api/v1/projects/', title);
    }

    function remove(project) {
      return $http.delete('/api/v1/projects/' + project.id + '/');
    }

    function get(username) {
      return $http.get('/api/v1/accounts/' + username + '/projects/');
    }

    function update(project) {
      return $http.put('/api/v1/projects/' +  project.id + '/', project);
    }

    function create_file(pro_id, folder_id, file) {
      return $http.post('/api/v1/files/', file, {headers: {'project': pro_id, 'folder': folder_id}});
    }

    function remove_file(file) {
      return $http.delete('/api/v1/files/' + file.id + '/');
    }

    function get_files(project_id, folder_id) {
      return $http.get('/api/v1/projects/' + project_id + '/files/', {headers: {'folder': folder_id}});
    }

    function update_file(file) {
      return $http.put('/api/v1/files/' +  file.id + '/', file);
    }

    function staticRun(data) {
      return $http.post('/api/v1/project/staticrun/', data);
    };

    function run(data) {
      return $http.post('/api/v1/project/run/', data);
    };

    function clone(git_command) {
      return $http.post('/api/v1/project/git-clone/', git_command);
    };

    function push(data) {
      return $http.post('/api/v1/project/git-push/', data);
    };
  }
})();
