(function () {
    'use strict';

    angular
        .module('pro1oh1.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider) {
        $routeProvider.when('/', {
            templateUrl: '/static/templates/home/home.html'
        }).when('/register', {
            controller: 'RegisterController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/register.html'
        }).when('/login', {
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/login.html'
        }).when('/quick-run', {
            templateUrl: '/static/templates/quick-run/quick-run.html'
        }).when('/compare', {
            templateUrl: '/static/templates/compare/compare.html'
        }).when('/my-projects', {
            templateUrl: '/static/templates/projects/projects.html'
        }).when('/my-projects/:project', {
            templateUrl: '/static/templates/projects/project.html'
        }).when('/tutorials', {
            templateUrl: '/static/templates/tutorials/tutorials.html'
        }).when('/show-off', {
            templateUrl: '/static/templates/show-off/show-off.html'
        }).when('/:username', {
            controller: 'ProfileController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/profiles/profile.html'
        }).when('/:username/settings', {
            controller: 'ProfileSettingsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/profiles/settings.html'
        }).otherwise('/');
    }
})();
