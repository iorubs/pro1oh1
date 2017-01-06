//QuickRunController
(function () {
  'use strict';

  angular
    .module('pro1oh1.quick-run.controllers')
    .controller('QuickRunController', [ '$scope', '$location', '$mdDialog', 'Snackbar', '$timeout', '$mdSidenav', '$log', 'QuickRun', function($scope, $location, $mdDialog, Snackbar, $timeout, $mdSidenav, $log, QuickRun) {

      if($location.path() == '/compare'){
        var tabs = [{title: 'App1', language: "Text"}, {title: 'App2', language: "Text"},];
        var editors = [];
        var selected = null;
        var previous = null;
        $scope.cmp_mode = true;
      }else{
        var tabs = [{title: 'Main', language: "Text"},];
        var editors = [];
        var selected = null;
        var previous = null;
        $scope.cmp_mode = false;
      }

      $scope.stats_default = [['time', 'CPU', 'Core1', 'Core2', 'Core3', 'Core4', 'RAM', 'DISK'],
      ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']];
      $scope.stats = $scope.stats_default;
      $scope.stats2 = $scope.stats_default;
      $scope.tabs = tabs;
      $scope.total_cpu_usage = 'n/a';
      $scope.total_cpu_usage2 = 'n/a';
      $scope.total_memory_usage = 'n/a';
      $scope.total_memory_usage2 = 'n/a';
      $scope.runtime = 'n/a';
      $scope.runtime2 = 'n/a';
      $scope.stats_interval = 1;
      StatsController($scope);
      $scope.update_stats();
      $scope.text = ["Output."];
      $scope.text2 = ["Output."];
      $scope.selectedIndex = 0;

      $scope.$watch( function () {
        if(window.innerHeight < 550)
          $scope.windowHeight = 600;
        else
          $scope.windowHeight = window.innerHeight;
      });

      $scope.$watch('selectedIndex', function(current, old){
        previous = selected;
        selected = tabs[current];
        if ( old + 1 && (old != current))
        if ( current + 1 )

        $scope.mode = selected.language;
      });

      $scope.addTab = function (title){
        if(title != undefined){
          var title_split = title.split(".");
          var language_index = $scope.mode_endings.indexOf(title_split[title_split.length-1]);
          var language = $scope.modes[language_index];

          if($scope.modes.indexOf(language) == -1)
            language = 'Text';

          tabs.push({ title: title, language: language, disabled: false});
          $scope.close();
        }
      };

      $scope.removeTab = function (){
        tabs.splice($scope.selectedIndex, 1);
        editors.splice($scope.selectedIndex, 1);
      };

      $scope.modes = ['Text', 'C++', 'Java', 'Python', 'Perl', 'Bash', 'Golang', 'ObjectiveC', 'Ruby', 'Scala', 'Lisp'];
      $scope.mode_endings = ['txt', 'cpp', 'java', 'py', 'prl', 'sh', 'go', 'm', 'rb', 'scala', 'lisp'];
      $scope.themes = ['chrome', 'cobalt', 'vibrant_ink'];
      $scope.mode = $scope.modes[0];
      $scope.theme = $scope.themes[0];
      $scope.auto_completion = true;

      $scope.$watch('auto_completion', function(current, old){
        for(var i=0; i<editors.length; i++)
            editors[i].setOptions({enableLiveAutocompletion: $scope.auto_completion});
      });

      // The ui-ace option
      $scope.aceOption = {
        onLoad: function (ace_editor) {
          ace_editor.setTheme("ace/theme/" + $scope.theme);
          ace_editor.setShowPrintMargin(false);
          ace_editor.getSession().setUseWrapMode(true);
          ace_editor.getSession().setWrapLimitRange(120, 120);
          ace_editor.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: $scope.auto_completion
          });
          editors.push(ace_editor); //store editor
        }
      };

      //Languages not ready for static analyses
      $scope.no_linter_langs = ['Text', 'Lisp'];
      $scope.no_linter = function (mode){
        return $scope.no_linter_langs.indexOf(mode) != -1;
      };

      //change editor mode(language)
      $scope.modeChanged = function (mode) {
        var lowercase_mode = mode.toLowerCase();
        if(lowercase_mode == 'c++')
          lowercase_mode = 'c_cpp'

        if(lowercase_mode == 'bash')
          editors[$scope.selectedIndex].getSession().setMode("ace/mode/sh");
        else
          editors[$scope.selectedIndex].getSession().setMode("ace/mode/" + lowercase_mode);

        var old_lang = tabs[$scope.selectedIndex].language;
        tabs[$scope.selectedIndex].language = mode;

        var new_title = tabs[$scope.selectedIndex].title;
        new_title = new_title.split(".");
        var file_type = $scope.mode_endings[$scope.modes.indexOf(mode)]
        if(file_type != 'txt')
          if(old_lang != 'Text')
            new_title[new_title.length-1] = file_type;
          else
            new_title.push(file_type);
        else
          new_title.splice(new_title.length-1, 1);


        tabs[$scope.selectedIndex].title = new_title.join('.');
      };

      $scope.wrapOptions = ['Off', '40', '80', '120', 'Free'];
      $scope.wrap_val = $scope.wrapOptions[3];

      //change wrap option
      $scope.setWrapOption = function (wrap_val){
        if(wrap_val == 'Off'){
          for (var i = 0; i < editors.length; i++)
            editors[i].getSession().setUseWrapMode(false);
        }else{
          if(wrap_val == 'Free'){
            for (var i = 0; i < editors.length; i++){
              editors[i].getSession().setUseWrapMode(true);
              editors[i].getSession().setWrapLimitRange();
            }
          }else{
            for (var i = 0; i < editors.length; i++){
              editors[i].getSession().setUseWrapMode(true);
              editors[i].getSession().setWrapLimitRange(wrap_val, wrap_val);
            }
          }
        }

        $scope.wrap_val = wrap_val;
      };

      $scope.changeTheme = function (new_theme) {
        for (var i = 0; i < editors.length; i++)
          editors[i].setTheme("ace/theme/" + new_theme);

        $scope.theme = new_theme;
      };

      // Initial code content...
      $scope.aceModel = 'Coding area obviously, dahhh :P';

      $scope.runningCode = false;
      $scope.runCancel = false;
      $scope.runCancel2 = false;

      $scope.cancelRun = function () {
        $scope.runCancel = false;
        $scope.runCancel2 = false;
        $scope.text = ["Execution cancelled."]
        $scope.text2 = ["Execution cancelled."]
        Snackbar.show('Execution cancelled.');
      }

      $scope.runningStatic = false;
      $scope.runningStatic2 = false;

      $scope.staticRun = function () {
        Snackbar.show('Static analysis.');
        $scope.runningStatic = true;

        var editor_value = editors[$scope.selectedIndex].getValue();
        var file_info = tabs[$scope.selectedIndex];

        if($scope.cmp_mode){
            editor_value = editors[0].getValue();
            file_info = tabs[0];
        }

        $scope.text = [""];

        QuickRun.staticRun(editor_value, file_info).then(function(response){
          $scope.text = response.data.output;
          $scope.runningStatic = false;
        });

        if($scope.cmp_mode){
          $scope.text2 = [""];
          $scope.runningStatic2 = true;
          editor_value = editors[1].getValue();
          file_info = tabs[1];

          QuickRun.staticRun(editor_value, file_info).then(function(response){
            $scope.text2 = response.data.output;
            $scope.runningStatic2 = false;
          });
        }
      }

      $scope.runCode = function () {
        Snackbar.show('Running code.');
        $scope.runningCode = true;
        var editor_values = [];
        $scope.text = [""]

        for (var i = 0; i < editors.length; i++)
          editor_values.push(editors[i].getValue());

        $scope.runCancel = true;

        var runnable = $scope.selectedIndex;
        if($scope.cmp_mode){
            runnable = 0;
            $scope.runCancel2 = true;
            $scope.text2 = [""]
        }

        QuickRun.runCode(editor_values, runnable, tabs).then(function(response){
          var runResults = response.data;
          if(runResults.ret_val != -1)
            $scope.stats = runResults.stats
          else
            $scope.stats = $scope.stats_default;

          if($scope.runCancel == true)
            $scope.text = response.data.output;

          $scope.runCancel = false;

          if($scope.stats.length > 30){
            var tmp = $scope.stats.length%30;
            tmp = $scope.stats.length-tmp;
            $scope.stats_interval = tmp/30 + 1;
          }
          else
            $scope.stats_interval = 1;

          if($scope.cmp_mode && $scope.runCancel2 == true){
            QuickRun.runCode(editor_values, 1, tabs).then(function(response){
              var runResults = response.data;
              if(runResults.ret_val != -1)
                $scope.stats2 = runResults.stats
              else
                $scope.stats2 = $scope.stats_default;

              if($scope.runCancel2 == true)
                $scope.text2 = response.data.output;

              $scope.runningCode = false;
              $scope.runCancel2 = false;

              if($scope.stats2.length > $scope.stats.length)
                if($scope.stats2.length > 30 ){
                  var tmp = $scope.stats2.length%30;
                  tmp = $scope.stats2.length-tmp;
                  $scope.stats_interval = tmp/30 + 1;
                }
                else
                  $scope.stats_interval = 1;

              $scope.update_stats();
            });
          }
          else{
            $scope.runningCode = false;
            $scope.update_stats();
          }
        });
      };

      $scope.toggleOptions = buildToggler('editorOptions');

      function buildToggler(navID){
        return function(){
          $mdSidenav(navID)
            .toggle()
        }
      }

      $scope.close = function()
      {
        $mdSidenav('editorOptions').close();
      };

      $scope.showAdvanced = function() {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: StatsController,
          templateUrl: 'stats.tmpl.html',
          clickOutsideToClose:true
        });
      };

      $scope.stats_more_detail = function() {
        if($scope.stats_interval > 1){
          $scope.stats_interval = $scope.stats_interval - 1;
          $scope.update_stats();
        }
      };

      $scope.stats_less_detail = function() {
        if($scope.stats_interval < 10){
          $scope.stats_interval = $scope.stats_interval + 1;
          $scope.update_stats();
        }
      };

      $scope.add = function() {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'add.tmpl.html',
          clickOutsideToClose:true
        })
      };
    }]);

    function DialogController($scope, $mdDialog) {
      $scope.cancel = function() {
        $mdDialog.cancel();
      };
    }

    function StatsController($scope, $mdDialog) {

      $scope.cancel = function() {
        $mdDialog.cancel();
      };

      $scope.getCpu = function(){
        /* CPU Usage */
        $scope.labels = [];
        $scope.series_cpu = ['CPU usage in nanoseconds'];
        $scope.data_cpu = [];
        $scope.cpu_usage = [];
        $scope.colors = ['#3498db'];

        $scope.labels.push('Start');
        $scope.cpu_usage.push('0');

        if($scope.stats.length > 2){
          for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval){
            $scope.labels.push(($scope.stats[i][0]) + ' sec');
            if(i == 1)
              $scope.cpu_usage.push(($scope.stats[1+$scope.stats_interval][1] - $scope.stats[$scope.stats_interval][1]) / 2);
            else
              $scope.cpu_usage.push($scope.stats[i][1] - $scope.stats[i-1][1]);
          }
        }

        $scope.labels.push('End');
        $scope.cpu_usage.push('0');
        $scope.data_cpu.push($scope.cpu_usage);

        if($scope.cmp_mode){
          $scope.colors.push('#e74c3c');
          $scope.series_cpu = [$scope.tabs[0].title, $scope.tabs[1].title];
          $scope.cpu_usage = [];
          $scope.cpu_usage.push('0');

          if($scope.stats2.length > 2){
            for (var i = $scope.stats_interval; i < $scope.stats2.length; i = i + $scope.stats_interval){
              if(i == 1)
                $scope.cpu_usage.push(($scope.stats2[1+$scope.stats_interval][1] - $scope.stats2[$scope.stats_interval][1]) / 2);
              else
                $scope.cpu_usage.push($scope.stats2[i][1] - $scope.stats2[i-1][1]);
            }
          }

          if($scope.stats2.length > $scope.stats.length){
            $scope.labels.length = 0;
            $scope.labels.push('Start');
            for (var i = $scope.stats_interval; i < $scope.stats2.length; i = i + $scope.stats_interval)
              $scope.labels.push(($scope.stats2[i][0]) + ' sec');
            $scope.labels.push('End');
          }
          $scope.cpu_usage.push('0');
          $scope.data_cpu.push($scope.cpu_usage);
        }
      }

      $scope.getRAM = function(){
        /* RAM Usage */
        $scope.series_ram = ['RAM usage in kilobytes'];
        $scope.data_ram = [];
        $scope.ram_usage = [];
        $scope.colors = ['#3498db'];
        $scope.ram_usage.push('0');

        for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval)
          $scope.ram_usage.push(($scope.stats[i][6]/1000).toFixed(2));

        $scope.ram_usage.push('0');
        $scope.data_ram.push($scope.ram_usage);

        if($scope.cmp_mode){
          $scope.colors.push('#e74c3c');
          $scope.series_ram = [$scope.tabs[0].title, $scope.tabs[1].title];
          $scope.ram_usage = [];

          $scope.ram_usage.push('0');

          for (var i = $scope.stats_interval; i < $scope.stats2.length; i = i + $scope.stats_interval)
            $scope.ram_usage.push(($scope.stats2[i][6]/1000).toFixed(2));

          $scope.ram_usage.push('0');
          $scope.data_ram.push($scope.ram_usage);
        }
      }

      $scope.getDiskIO = function(){
        /* DISK IO Usage */
        $scope.series_disk = ['DISK Memory usage in bytes'];
        $scope.data_disk = [];
        $scope.disk_io_usage = [];
        $scope.colors = ['#3498db'];
        $scope.disk_io_usage.push('0');

        for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval)
          $scope.disk_io_usage.push($scope.stats[i][7]);

        $scope.disk_io_usage.push('0');
        $scope.data_disk.push($scope.disk_io_usage);

        if($scope.cmp_mode){
          $scope.colors.push('#e74c3c');
          $scope.series_disk = [$scope.tabs[0].title, $scope.tabs[1].title];
          $scope.disk_io_usage = [];
          $scope.disk_io_usage.push('0');

          for (var i = $scope.stats_interval; i < $scope.stats2.length; i = i + $scope.stats_interval)
            $scope.disk_io_usage.push($scope.stats2[i][7]);

          $scope.disk_io_usage.push('0');
          $scope.data_disk.push($scope.disk_io_usage);
        }
      }

      $scope.coreOvertime = function(){
        /* Core Usage */
          $scope.series_core = ['Core1', 'Core2', 'Core3', 'Core4'];
          $scope.data_core = [];

          $scope.core_1 = ['0'];
          $scope.core_2 = ['0'];
          $scope.core_3 = ['0'];
          $scope.core_4 = ['0'];

          if($scope.stats.length > 2){
            for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval){
              if(i==1){
                $scope.core_1.push(($scope.stats[1+$scope.stats_interval][2] - $scope.stats[$scope.stats_interval][2]) / 2);
                $scope.core_2.push(($scope.stats[1+$scope.stats_interval][3] - $scope.stats[$scope.stats_interval][3]) / 2);
                $scope.core_3.push(($scope.stats[1+$scope.stats_interval][4] - $scope.stats[$scope.stats_interval][4]) / 2);
                $scope.core_4.push(($scope.stats[1+$scope.stats_interval][5] - $scope.stats[$scope.stats_interval][5]) / 2);
              }else{
                $scope.core_1.push($scope.stats[i][2] - $scope.stats[i-1][2]);
                $scope.core_2.push($scope.stats[i][3] - $scope.stats[i-1][3]);
                $scope.core_3.push($scope.stats[i][4] - $scope.stats[i-1][4]);
                $scope.core_4.push($scope.stats[i][5] - $scope.stats[i-1][5]);
              }
            }
          }

          $scope.core_1.push('0');
          $scope.core_2.push('0');
          $scope.core_3.push('0');
          $scope.core_4.push('0');

          $scope.data_core.push($scope.core_1);
          $scope.data_core.push($scope.core_2);
          $scope.data_core.push($scope.core_3);
          $scope.data_core.push($scope.core_4);
      }

      $scope.getCore = function(){
        /* Core Total usage */
        $scope.labels_core_total = ['Core1', 'Core2', 'Core3', 'Core4'];
        $scope.data_core_total = [];
        $scope.core_line_options = {datasetFill : false}

        var totals_index = $scope.stats.length-1;
        $scope.data_core_total.push($scope.stats[totals_index][2]);
        $scope.data_core_total.push($scope.stats[totals_index][3]);
        $scope.data_core_total.push($scope.stats[totals_index][4]);
        $scope.data_core_total.push($scope.stats[totals_index][5]);

        if($scope.cmp_mode){
          $scope.data_core_total2 = [];

          totals_index = $scope.stats2.length-1;
          $scope.data_core_total2.push($scope.stats2[totals_index][2]);
          $scope.data_core_total2.push($scope.stats2[totals_index][3]);
          $scope.data_core_total2.push($scope.stats2[totals_index][4]);
          $scope.data_core_total2.push($scope.stats2[totals_index][5]);
        }
      }

      $scope.update_stats = function(){
        /* update stats */

        var totals_index = $scope.stats.length-1;

        if(totals_index > 0){
          $scope.total_cpu_usage = $scope.stats[totals_index][1];
          $scope.total_memory_usage = $scope.stats[totals_index][6];
          $scope.runtime = $scope.stats[totals_index][0];
        }else{
          $scope.total_cpu_usage = 'n/a';
          $scope.total_memory_usage = 'n/a';
          $scope.runtime = 'n/a';
        }

        if($scope.cmp_mode){
          var totals_index = $scope.stats2.length-1;

          if(totals_index > 0){
            $scope.total_cpu_usage2 = $scope.stats2[totals_index][1];
            $scope.total_memory_usage2 = $scope.stats2[totals_index][6];
            $scope.runtime2 = $scope.stats2[totals_index][0];
          }else{
            $scope.total_cpu_usage2 = 'n/a';
            $scope.total_memory_usage2 = 'n/a';
            $scope.runtime2 = 'n/a';
          }
        }

        $scope.getCpu();
        $scope.getRAM();
        $scope.getDiskIO();
        $scope.coreOvertime();
        $scope.getCore();
      }
    }
})();
