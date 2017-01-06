//QuickRun
(function () {
  'use strict';

  angular
    .module('pro1oh1.quick-run.services')
    .factory('QuickRun', ['$http', function ($http) {

      var QuickRun = {
        runCode: runCode,
        staticRun: staticRun
      };

      return QuickRun;

      //run code
      function runCode(files, mainIndex, fileInfo) {
        var json = {'files': files, 'index': mainIndex, 'info': fileInfo};

        return $http.post('/api/v1/quick-run/singlerun/', json);
      };

      //static run
      function staticRun(file, fileInfo) {
        var json = {'file': file, 'info': fileInfo};

        return $http.post('/api/v1/quick-run/staticrun/', json);
      };
    }]);
})();
