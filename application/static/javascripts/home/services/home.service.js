(function () {
  'use strict';

  angular
    .module('pro1oh1.home.services')
    .factory('Home', Home);

  Home.$inject = ['$http'];

  function Home($http) {
    var Home = {
      user_count: user_count
    };

    return Home;

    function user_count() {
      return $http.get('api/v1/user-count/');
    }

  }
})();
