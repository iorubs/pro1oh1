(function () {
    'use strict';

    angular
        .module('pro1oh1', [
            'pro1oh1.config',
            'pro1oh1.routes',
            'pro1oh1.authentication',
            'pro1oh1.layout',
            'pro1oh1.profiles',
            'pro1oh1.utils',
            'pro1oh1.quick-run',
            'pro1oh1.projects',
            'pro1oh1.tutorials',
            'pro1oh1.home',
        ])
        .run(run);

    run.$inject = ['$http'];

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    angular
        .module('pro1oh1.config', []);

    angular
        .module('pro1oh1.routes', ['ngRoute']);
})();
