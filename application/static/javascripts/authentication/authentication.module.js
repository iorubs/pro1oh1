(function () {
    'use strict';

    angular
        .module('pro1oh1.authentication', [
            'pro1oh1.authentication.controllers',
            'pro1oh1.authentication.services'
        ]);

    angular
        .module('pro1oh1.authentication.controllers', []);

    angular
        .module('pro1oh1.authentication.services', ['ngCookies']);
})();
