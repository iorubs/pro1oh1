(function () {
  'use strict';

  angular
    .module('pro1oh1.tutorials', [
      'pro1oh1.tutorials.controllers',
      'pro1oh1.tutorials.services'
    ]);

  angular
    .module('pro1oh1.tutorials.controllers', [
      'ngMaterial',
      'youtube-embed'
    ]);

  angular
    .module('pro1oh1.tutorials.services', []);
})();
