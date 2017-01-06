//HomeController
(function () {
  'use strict';

  angular
    .module('pro1oh1.home.controllers')
    .controller('HomeController', [ '$scope', 'Home', 'parallaxHelper', function($scope, Home, parallaxHelper) {

      $scope.docker_x = parallaxHelper.createAnimator(2);
      $scope.info_y = parallaxHelper.createAnimator(0.5);

      $scope.myPattern = '/static/templates/home/images/Turtle-48.png'

      Home.user_count().then(getUserCountSuccessFn, getUserCountErrorFn);

       function getUserCountSuccessFn(data, status, headers, config) {
         $scope.user_count = data.data;
       }

       function getUserCountErrorFn(data, status, headers, config) {
         Snackbar.error('Could not get user count.');
       }

    }]);
})();
