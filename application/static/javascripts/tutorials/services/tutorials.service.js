//Tutorials
(function () {
  'use strict';

  angular
    .module('pro1oh1.tutorials.services')
    .factory('Tutorials', ['$http', function ($http) {

      var Tutorials = {
        create_group: create_group,
        remove_group: remove_group,
        get_groups: get_groups,
        update_group: update_group,
        create_tutorial: create_tutorial,
        remove_tutorial: remove_tutorial,
        get_tutorials: get_tutorials,
        update_tutorial: update_tutorial
      };

      return Tutorials;

      function create_group(t_group) {
        return $http.post('/api/v1/tutorial_groups/', t_group);
      }

      function remove_group(t_group) {
        return $http.delete('/api/v1/tutorial_groups/' + t_group.id + '/');
      }

      function get_groups() {
        return $http.get('/api/v1/tutorial_groups/');
      }

      function update_group(t_group) {
        return $http.put('/api/v1/tutorial_groups/' +  t_group.id + '/', t_group);
      }

      function create_tutorial(tutorial) {
        return $http.post('/api/v1/tutorials/', tutorial);
      }

      function remove_tutorial(tutorial) {
        return $http.delete('/api/v1/tutorials/' + tutorial.id + '/');
      }

      function get_tutorials(t_group) {
        return $http.get('/api/v1/tutorial_groups/' + t_group.id + '/tutorials/');
      }

      function update_tutorial(tutorial) {
        return $http.put('/api/v1/tutorials/' +  tutorial.id + '/', tutorial);
      }
    }]);
})();
