/**
* NavbarController for logging out users
*/
(function () {
    'use strict';

    angular
        .module('pro1oh1.layout.controllers')
        .controller('NavbarController', NavbarController);

    NavbarController.$inject = ['$scope', 'Authentication'];

    function NavbarController($scope, Authentication) {
        var vm = this;

        vm.logout = logout;

        //Log the user out
        function logout() {
            Authentication.logout();
        }

        $(document).on('click','.navbar-collapse.in',function(e) {
          if( $(e.target).is('a') )
              $(this).collapse('hide');
        });
    }
})();
