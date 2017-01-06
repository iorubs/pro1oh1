/**
* Authentication
*/
(function () {
    'use strict';

    angular
        .module('pro1oh1.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookies', '$http'];

    function Authentication($cookies, $http) {
      var Authentication = {
        getAuthenticatedAccount: getAuthenticatedAccount,
        isAuthenticated: isAuthenticated,
        login: login,
        logout: logout,
        register: register,
        setAuthenticatedAccount: setAuthenticatedAccount,
        unauthenticate: unauthenticate
      };

      return Authentication;

      //register user
      function register(email, password, username, first_name, last_name) {
        return $http.post('/api/v1/accounts/', {
          username: username,
          password: password,
          email: email,
          first_name: first_name,
          last_name: last_name
        });
      }

      // login user
      function login(username, password) {
        return $http.post('/api/v1/auth/login/', {
          username: username, password: password
        });
      }

      function getAuthenticatedAccount() {
        if (!$cookies.get('authenticatedAccount')) {
          return;
        }

        return JSON.parse($cookies.get('authenticatedAccount'));
      }

      function isAuthenticated() {
        return !!$cookies.get('authenticatedAccount');
      }

      function setAuthenticatedAccount(account) {
        $cookies.putObject('authenticatedAccount', account);
      }

      function unauthenticate() {
        $cookies.remove('authenticatedAccount');
      }

      // logout user
      function logout() {
        return $http.post('/api/v1/auth/logout/')
            .then(logoutSuccessFn, logoutErrorFn);

        function logoutSuccessFn(data, status, headers, config) {
            Authentication.unauthenticate();
            window.location = '/';
        }

        function logoutErrorFn(data, status, headers, config) {
            console.error('Epic failure!');
        }
      }
    }
})();
