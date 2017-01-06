(function () {
    'use strict';

    angular
        .module('pro1oh1.quick-run', [
            'pro1oh1.quick-run.controllers',
            'pro1oh1.quick-run.services'
        ]);

    angular
        .module('pro1oh1.quick-run.controllers', [
            'ui.ace',
            'ngMaterial',
            'chart.js'
        ]);

    angular
        .module('pro1oh1.quick-run.services', ['ngCookies']);
})();
