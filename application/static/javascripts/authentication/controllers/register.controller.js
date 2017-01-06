(function () {
    'use strict';

    angular
        .module('pro1oh1.authentication.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', '$scope', '$mdDialog', 'Authentication'];

    function RegisterController($location, $scope, $mdDialog, Authentication) {
      var vm = this;
      vm.register = register;

      $scope.pass2_field_color = "";

      function register() {
        if(vm.password != vm.password2){
          $scope.pass2_field_color = "red";
          $scope.error_message = "Passwords must match.";
        }
        else
          Authentication.register(vm.email, vm.password, vm.username, vm.username, vm.username).then(registerSuccessFn, registerErrorFn);
      }

      function registerSuccessFn(data, status, headers, config) {
        Authentication.login(vm.username, vm.password).then(loginSuccessFn, loginErrorFn);
      }

      function registerErrorFn(data, status, headers, config) {
        console.error(data);
      }

      function loginSuccessFn(data, status, headers, config) {
        Authentication.setAuthenticatedAccount(data.data);
        window.location = '/';
      }

      function loginErrorFn(data, status, headers, config) {
        console.error('Epic failure!');
      }

  		activate();

  		function activate() {
        // If the user is authenticated, they should not be here.
        if (Authentication.isAuthenticated()) {
          $location.url('/');
        }
  		}
    }

    function DialogController($scope, $mdDialog) {
      $scope.cancel = function() {
        $mdDialog.cancel();
      };
    }
})();
