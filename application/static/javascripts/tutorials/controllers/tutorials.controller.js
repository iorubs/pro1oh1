//TutorialsController
(function () {
  'use strict';

  angular
    .module('pro1oh1.tutorials.controllers')
    .controller('TutorialsController', [ '$scope', 'Snackbar', '$mdDialog', 'Tutorials', 'Authentication', 'youtubeEmbedUtils', function($scope, Snackbar, $mdDialog, Tutorials, Authentication, youtubeEmbedUtils) {

      var authenticatedAccount = Authentication.getAuthenticatedAccount();
      $scope.admin_mode = false;

      if(authenticatedAccount && authenticatedAccount.is_admin)
        $scope.admin_mode = true;

      $scope.$watch( function () {
        if(window.innerHeight < 600)
          $scope.windowHeight = 600;
        else
          $scope.windowHeight = window.innerHeight;
      });

      $scope.theBestVideo = 'https://www.youtube.com/watch?v=rdxfC-yHIP8';
      $scope.playerVars = {
        controls: 2,
        autohide: 0,
        autoplay: 0
      };

      $scope.view_mode = true;

      $scope.change_view = function () {
        $scope.view_mode=!$scope.view_mode;
      }

      $scope.groups = [];
      $scope.tutorials = [];

      Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);

      function getGroupSuccessFn(data, status, headers, config) {
        $scope.groups = data.data;
        Tutorials.get_tutorials($scope.groups[index]).then(getTutorialSuccessFn, getTutorialErrorFn);
      }

      function getGroupErrorFn(data, status, headers, config) {
        Snackbar.error("Couldn't find tutorials!");
      }

      var index=0;

      function getTutorialSuccessFn(data, status, headers, config) {
        index = index+1;
        $scope.tutorials.push(data.data);

        if(index < $scope.groups.length)
          Tutorials.get_tutorials($scope.groups[index]).then(getTutorialSuccessFn, getTutorialErrorFn);
        else
          index=0;
      }

      function getTutorialErrorFn(data, status, headers, config) {
        Snackbar.error("Couldn't find tutorials!");
      }

      $scope.group;
      var group_id;
      var group_index;
      $scope.tutorial;

      $scope.select_group = function (index) {
        $scope.group = $scope.groups[index];
        group_id = $scope.group.id;
        group_index = index;
        $scope.tutorial = undefined;
      }

      $scope.open_tutorial = function (index) {
        $scope.tutorial = $scope.tutorials[group_index][index];
        $scope.group = undefined;
        $scope.theBestVideo = $scope.tutorial.url;
      }

      /*Group manager functions*/

      $scope.add_group = function () {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'add.group.tmpl.html',
          clickOutsideToClose:true
        })
      }

     $scope.submit_group = function(title, info) {
       Tutorials.create_group({'title': title, 'info': info}).then(createGroupSuccessFn, createGroupErrorFn);
       $mdDialog.cancel();
     }

      function createGroupSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.tutorials = [];
        Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);
      }

      function createGroupErrorFn(data, status, headers, config) {
        Snackbar.error('Error!');
      }

      $scope.remove_group = function () {
        Tutorials.remove_group($scope.group).then(removeGroupSuccessFn, removeGroupErrorFn);
      }

      function removeGroupSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.group = undefined;
        $scope.tutorials = [];
        Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);
      }

      function removeGroupErrorFn(data, status, headers, config) {
        Snackbar.error('Error!');
      }

      $scope.update_group = function () {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'update.group.tmpl.html',
          clickOutsideToClose:true
        })
      }

      $scope.submit_update_group = function (title, info) {
        if(title != undefined)
          $scope.group.title = title;
        if(info != undefined)
          $scope.group.info = info;

        Tutorials.update_group($scope.group).then(updateGroupSuccessFn, updateGroupErrorFn);
        $mdDialog.cancel();
      }

      function updateGroupSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.tutorials = [];
        Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);
      }

      function updateGroupErrorFn(data, status, headers, config) {
        Snackbar.error('Error!');
      }

      /*Tutorial manager functions*/

      $scope.add_tutorial = function () {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'add.tutorial.tmpl.html',
          clickOutsideToClose:true
        })
      }

      $scope.submit_tutorial = function (title, url) {
        Tutorials.create_tutorial({'t_group': group_id, 'title': title, 'url': url}).then(createTutorialSuccessFn, createTutorialErrorFn);
        $mdDialog.cancel();
      }

      function createTutorialSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.tutorials = [];
        Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);

      }

      function createTutorialErrorFn(data, status, headers, config) {
        Snackbar.error('Error!');
      }

      $scope.remove_tutorial = function () {
        Tutorials.remove_tutorial($scope.tutorial).then(removeTutorialSuccessFn, removeTutorialErrorFn);
      }

      function removeTutorialSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.tutorial = undefined;
        $scope.tutorials = [];
        Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);
      }

      function removeTutorialErrorFn(data, status, headers, config) {
        Snackbar.error('Error!');
      }

      $scope.update_tutorial = function () {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'update.tutorial.tmpl.html',
          clickOutsideToClose:true
        })
      }

      $scope.submit_update_tutorial = function (title, url) {
        if(title != undefined)
          $scope.tutorial.title = title;
        if(url != undefined)
          $scope.tutorial.url = url;

        Tutorials.update_tutorial($scope.tutorial).then(updateTutorialSuccessFn, updateTutorialErrorFn);
        $mdDialog.cancel();
      }

      function updateTutorialSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.tutorials = [];
        Tutorials.get_groups().then(getGroupSuccessFn, getGroupErrorFn);
      }

      function updateTutorialErrorFn(data, status, headers, config) {
        Snackbar.error('Error!');
      }
    }]);

    function DialogController($scope, $mdDialog) {
      $scope.cancel = function() {
        $mdDialog.cancel();
      };
    }
})();
