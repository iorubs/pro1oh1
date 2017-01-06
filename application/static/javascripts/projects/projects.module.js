(function () {
  'use strict';

  angular
    .module('pro1oh1.projects', [
      'pro1oh1.projects.controllers',
      'pro1oh1.projects.services'
    ]);

  angular
    .module('pro1oh1.projects.controllers', [
      'ngMaterial',
      'angularResizable',
      'angularBootstrapNavTree',
      'ui.ace'
    ]);

  angular
    .module('pro1oh1.projects.services', []);
})();
