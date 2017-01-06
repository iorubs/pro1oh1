(function () {
    'use strict';

    angular
        .module('pro1oh1.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', '$scope', 'Authentication'];

    // LoginController
    function LoginController($location, $scope, Authentication) {
      var vm = this;
      vm.login = login;
      activate();

      function activate() {
        // If the user isn't authenticated, they should not be here.
        if (Authentication.isAuthenticated()) {
          $location.url('/');
        }
      }

      //Log the user in
      function login() {
        Authentication.login(vm.username, vm.password).then(loginSuccessFn, loginErrorFn);
      }

      function loginSuccessFn(data, status, headers, config) {
        Authentication.setAuthenticatedAccount(data.data);
        window.location = '/';
      }

      function loginErrorFn(data, status, headers, config) {
        $scope.error_message = data.data.message;
      }
    }
})();
