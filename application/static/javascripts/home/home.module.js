(function () {
    'use strict';

    angular
        .module('pro1oh1.home', [
            'pro1oh1.home.controllers',
            'pro1oh1.home.services'
        ]);

    angular
        .module('pro1oh1.home.controllers', ['duParallax', 'ngParallax']);

    angular
        .module('pro1oh1.home.services', ['ngCookies']);
})();
