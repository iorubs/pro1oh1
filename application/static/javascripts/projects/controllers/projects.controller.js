//QuickRunController
(function () {
  'use strict';

  angular
    .module('pro1oh1.projects.controllers')
    .controller('ProjectsController', [ '$scope', '$location', '$log', '$mdDialog', '$mdSidenav', 'Snackbar', 'Projects', 'Authentication', function($scope, $location, $log, $mdDialog, $mdSidenav, Snackbar, Projects, Authentication) {

      $scope.projects = [];
      $scope.project = null;
      $scope.files_tree = [];
      $scope.selected_node = null;
      $scope.selected_branch = null;
      $scope.selected_root = null;
      $scope.hide_tree = false;
      var open_files = [];
      var open_branches = [];
      var selected;
      var previous;
      $scope.tabs = [];
      $scope.selectedIndex = -1;

      var authenticatedAccount = Authentication.getAuthenticatedAccount();

      //Snackbar.show(response.data);
      //$log.debug(!!authenticatedAccount);

      $scope.$watch( function () {
        if(window.innerHeight < 550)
          $scope.windowHeight = 550;
        else
          $scope.windowHeight = window.innerHeight;
      });

      function get_pro_list() {
        Projects.get(authenticatedAccount.username).then(function(response){
          for(var i=0; i<response.data.length; i++){
            $scope.projects.push(response.data[i]);
          }
        });
      }

      function get_files_list() {
        Projects.get(authenticatedAccount.username).then(function(response){
          var i=0;
          while(i<response.data.length){
            if(response.data[i].title == $location.path().substr(13))
              $scope.project = response.data[i];
            i++;
          }

          if($scope.project == null)
            window.location = '/my-projects';

          $scope.files_tree.push({
            label: $scope.project.title,
            onSelect: function(branch){
              $scope.selected_node = $scope.project;
              $scope.selected_root = true;
              get_children(branch, 'None');
              $scope.selected_branch = branch;
            },
            noLeaf: true
          });
        });
      }

      //Fetch file and on select add it to the editor
      function new_node(dir, data) {
        return {
          label: data.title,
          onSelect: function(branch){
            $scope.selected_node = branch.data;
            $scope.selected_root = false;
            if($scope.selected_node.f_type == 'folder')
              get_children(branch, $scope.selected_node.id);
            else{
              if(open_files.indexOf(branch.data.id) == -1){
                open_branches.push(branch);
                $scope.tabs.push({title: branch.data.title, content: branch.data.content, node: branch.data, save_status: false, set_points: false, point_start: 'start', point_end: 'end'});
                open_files.push(branch.data.id);
                $scope.mode = $scope.modes[mode_endings.indexOf(branch.data.f_type)];
              }
              else {
                $scope.selectedIndex = open_files.indexOf(branch.data.id);
              }
            }
            $scope.selected_branch = branch;
          },
          data: data,
          noLeaf: dir
        };

      }

      function get_children(branch, folder_id) {
        Projects.get_files($scope.project.id, folder_id).then(function(response){
          var this_children = [];
          for(var i=0; i<response.data.length; i++)
            this_children.push(new_node((response.data[i].f_type == 'folder'), response.data[i]));
          branch.children = this_children;
        });
      }

      if(!authenticatedAccount)
        window.location = '/login';
      else
        if($location.path() == '/my-projects')
          get_pro_list();
        else
          get_files_list();

      $scope.new_proj = function (title) {
        if($scope.projects.length < 8)
          Projects.create({'title': title}).then(createProjectSuccessFn, createProjectErrorFn);
        else
          Snackbar.error('You have reached the maximum number or projects.');
      }

      function createProjectSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! Project created.');
        $scope.projects = [];
        get_pro_list();
      }

      function createProjectErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to create project.');
      }

      $scope.gitBranch = 'master';

      $scope.clone_proj = function (url, branch, username, password) {
        var git_command = 'git clone ';

        if(branch == '')
          git_command += '-b master https://';
        else
          git_command += '-b ' + branch + ' https://';

        if(username != undefined && password != undefined && username != '' && password != '') {
          git_command += username + ':';
          git_command += password + '@';
        }

        var clean_url = url.split('https://');
        git_command += clean_url[clean_url.length-1];

        Snackbar.show('Cloning project.');

        $scope.clonning = true;

        Projects.clone({'git_clone' : git_command}).then(cloneProjectSuccessFn, cloneProjectErrorFn);
      }

      function cloneProjectSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! Project cloned.');
        $scope.projects = [];
        $scope.clonning = false;
        get_pro_list();
      }

      function cloneProjectErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to clone project.');
        $scope.clonning = false;
      }

      $scope.git_commit = function () {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'commit.tmpl.html',
          clickOutsideToClose:true
        })
      }

      $scope.git_push = function (message) {
        $scope.pushing = true;
        Projects.push({'project': $scope.project.id, 'message': message}).then(pushProjectSuccessFn, pushProjectErrorFn);
      }

      function pushProjectSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! Project pushed.');
        $mdDialog.cancel();
        $scope.pushing = false;
      }

      function pushProjectErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to push project.');
        $mdDialog.cancel();
        $scope.pushing = false;
      }

      $scope.open = function(id) {
        window.location = '/my-projects/' + $scope.projects[id].title;
      };

      $scope.add = function() {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'add.tmpl.html',
          clickOutsideToClose:true
        })
      };

      $scope.create_file = function(title) {
        $mdDialog.cancel();
        var folder_id = 'None';
        if(!$scope.selected_root)
          folder_id = $scope.selected_node.id;

        Projects.create_file($scope.project.id, folder_id, {'title': title, 'content': ' ', 'f_type': 'txt'}).then(createFileSuccessFn, createFileErrorFn);
      }

      function add_new_child(data){
        $scope.selected_branch.children.push(new_node((data.data.f_type == 'folder'), data.data));
      }

      function createFileSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! File created.');
        add_new_child(data);
      }

      function createFileErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to create file.');
      }

      $scope.create_folder = function(title) {
        $mdDialog.cancel();
        var folder_id = 'None';
        if(!$scope.selected_root)
          folder_id = $scope.selected_node.id;

        Projects.create_file($scope.project.id, folder_id, {'title': title, 'content': ' ', 'f_type': 'folder'}).then(createFolderSuccessFn, createFolderErrorFn);
      }

      function createFolderSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! Folder created.');
        add_new_child(data);
      }

      function createFolderErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to create folder.');
      }

      $scope.remove = function(ev) {
        if($scope.selected_root){
          var confirm = $mdDialog.confirm()
            .title('Project Killer!')
            .content('Would you like to delete your project?')
                .ariaLabel('Delete project.')
                .targetEvent(ev)
                .ok('Yes')
                .cancel('No');
          $mdDialog.show(confirm).then(function() {
            Projects.remove($scope.project).then(removeProjectSuccessFn, removeProjectErrorFn);
          }, function() {
            //cancel
          });
        }else{
          Projects.remove_file($scope.selected_node).then(removeFileSuccessFn, removeFileErrorFn);
        }
      };

      function removeProjectSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! Project removed.');
        window.location = '/my-projects';
      }

      function removeProjectErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to remove project.');
      }

      function remove_child(branch, uid) {
        var i = 0;
        while(branch.children[i].uid != uid)
          i++;
        branch.children.splice(i, 1);
      }

      function find_parent(branch, parent_uid, uid) {
        if(branch.uid == parent_uid)
          remove_child(branch, uid)
        else
          for(var i=0; i<branch.children.length; i++)
            find_parent(branch.children[i], parent_uid, uid)
      }

      function removeFileSuccessFn(data, status, headers, config) {
        var index = open_files.indexOf($scope.selected_branch.data.id);
        if(index != -1){
          open_files.splice(index, 1);
          $scope.tabs.splice(index, 1);
          open_branches.splice(index, 1);
        }

        Snackbar.show('Success! File removed.');
        find_parent($scope.files_tree[0], $scope.selected_branch.parent_uid, $scope.selected_branch.uid);
      }

      function removeFileErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to remove file.');
      }

      $scope.close_file_tree = function() {
        $scope.hide_tree = true;
      };

      $scope.open_file_tree = function() {
        $scope.hide_tree = false;
      };

      $scope.$watch('selectedIndex', function(current, old){
        if($scope.tabs[current] != undefined){
          previous = selected;
          selected = $scope.tabs[current];
          if(new_editor_tab){
            editors[current].setValue(open_branches[current].data.content);
            editors[current].clearSelection();
          }
          else
            editors[current].setSession(editors[current].getSession());

          $scope.new_changes = $scope.tabs[current].save_status;
          $scope.pointset = $scope.tabs[current].set_points;
          $scope.point_start = $scope.tabs[current].point_start;
          $scope.point_end = $scope.tabs[current].point_end;
          $scope.mode = $scope.modes[mode_endings.indexOf(open_branches[current].data.f_type)];
        }
      });

      var editors = [];
      $scope.new_changes = false;
      $scope.modes = ['Text', 'C++', 'Java', 'Python', 'Perl', 'Bash', 'Golang', 'ObjectiveC', 'Ruby', 'Scala', 'Lisp'];
      $scope.mode = $scope.modes[0];
      var mode_endings = ['txt', 'cpp', 'java', 'py', 'prl', 'sh', 'go', 'm', 'rb', 'scala', 'lisp'];
      $scope.themes = ['chrome', 'cobalt', 'vibrant_ink'];
      $scope.theme = $scope.themes[0];
      $scope.wrapOptions = ['Off', '40', '80', '120', 'Free'];
      $scope.wrap_val = $scope.wrapOptions[3];
      var new_editor_tab = false;
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
          ace_editor.getSession().setWrapLimitRange($scope.wrap_val, $scope.wrap_val);
          var lowercase_mode = $scope.mode.toLowerCase();
          if(lowercase_mode == 'c++')
            lowercase_mode = 'c_cpp'

          if (lowercase_mode == 'bash')
            ace_editor.getSession().setMode("ace/mode/sh");
          else
            ace_editor.getSession().setMode("ace/mode/" + lowercase_mode);
          new_editor_tab = true;
          ace_editor.on("change", function(change) {
            if(!new_editor_tab){
              $scope.new_changes = true;
              $scope.tabs[$scope.selectedIndex].save_status = true;
            }
            new_editor_tab = false;
          });
          ace_editor.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: $scope.auto_completion
          });
          editors.push(ace_editor); //store editor
        }
      };

      //Languages not ready for breakpoint analyses
      $scope.no_break_langs = ['Text', 'C++', 'Bash', 'Golang', 'ObjectiveC', 'Perl', 'Ruby', 'Scala', 'Lisp'];
      $scope.no_break_points = function (mode){
        return $scope.no_break_langs.indexOf(mode) != -1;
      };

      //Languages not ready for static analyses
      $scope.no_linter_langs = ['Text', 'Lisp'];
      $scope.no_linter = function (mode){
        return $scope.no_linter_langs.indexOf(mode) != -1;
      };

      $scope.removeTab = function (){
        $scope.tabs.splice($scope.selectedIndex, 1);
        editors.splice($scope.selectedIndex, 1);
        open_files.splice($scope.selectedIndex, 1);
        open_branches.splice($scope.selectedIndex, 1);

        $scope.selectedIndex = $scope.selectedIndex-1;

        console.log($scope.selectedIndex);

        if($scope.tabs.length == 0){
          $scope.hide_tree = false;
        }
        else{
          $scope.mode = $scope.modes[mode_endings.indexOf($scope.tabs[$scope.selectedIndex].node.f_type)];
          $scope.new_changes = $scope.tabs[$scope.selectedIndex].save_status;
          $scope.pointset = $scope.tabs[$scope.selectedIndex].set_points;
          $scope.point_start = $scope.tabs[$scope.selectedIndex].point_start;
          $scope.point_end = $scope.tabs[$scope.selectedIndex].point_end;
        }
      };

      //change editor mode(language)
      $scope.modeChanged = function (mode) {
        var lowercase_mode = mode.toLowerCase();

        if(lowercase_mode == 'c++')
          lowercase_mode = 'c_cpp'

          if (lowercase_mode == 'bash')
            editors[$scope.selectedIndex].getSession().setMode("ace/mode/sh");
          else
            editors[$scope.selectedIndex].getSession().setMode("ace/mode/" + lowercase_mode);

        var new_title = $scope.tabs[$scope.selectedIndex].title;
        new_title = new_title.split(".");

        var file_type = mode_endings[$scope.modes.indexOf(mode)]

        if(file_type != 'txt')
          if(open_branches[$scope.selectedIndex].data.f_type == 'txt')
            new_title.push(file_type);
          else
            new_title[new_title.length-1] = file_type;
        else
          new_title.splice(new_title.length-1, 1);

        open_branches[$scope.selectedIndex].data.f_type = file_type;
        $scope.tabs[$scope.selectedIndex].title = new_title.join('.');
        open_branches[$scope.selectedIndex].data.title = $scope.tabs[$scope.selectedIndex].title;
        open_branches[$scope.selectedIndex].label = $scope.tabs[$scope.selectedIndex].title;
        $scope.new_changes = true;
        $scope.tabs[$scope.selectedIndex].save_status = true;
      };


      $scope.save_file = function (){
        $scope.new_changes = false;
        $scope.tabs[$scope.selectedIndex].save_status = false;
        open_branches[$scope.selectedIndex].data.content = editors[$scope.selectedIndex].getValue();
        Projects.update_file(open_branches[$scope.selectedIndex].data).then(updateFileSuccessFn, updateFileErrorFn);
      };


      function updateFileSuccessFn(data, status, headers, config) {
        Snackbar.show('Success! File updated.');
      }

      function updateFileErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to update file.');
      }

      $scope.toggleOptions = buildToggler('editorOptions');

      function buildToggler(navID){
        return function(){
          $mdSidenav(navID)
            .toggle()
        }
      }

      $scope.close = function(){
        $mdSidenav('editorOptions').close();
      };

      $scope.changeTheme = function (new_theme) {
        for (var i = 0; i < editors.length; i++)
          editors[i].setTheme("ace/theme/" + new_theme);
        $scope.theme = new_theme;
      };

      //change wrap option
      $scope.setWrapOption = function (new_wrap_val){
        if(new_wrap_val == 'Off')
          for (var i = 0; i < editors.length; i++)
            editors[i].getSession().setUseWrapMode(false);
        else
          if(new_wrap_val == 'Free')
            for (var i = 0; i < editors.length; i++){
              editors[i].getSession().setUseWrapMode(true);
              editors[i].getSession().setWrapLimitRange();
            }
          else
            for (var i = 0; i < editors.length; i++){
              editors[i].getSession().setUseWrapMode(true);
              editors[i].getSession().setWrapLimitRange(new_wrap_val, new_wrap_val);
            }

        $scope.wrap_val = new_wrap_val;
      };

      $scope.runningStatic = false;

      $scope.staticRun = function (){
        $scope.runningStatic = true;
        $scope.text = []
        var data = {'id' : open_branches[$scope.selectedIndex].data.id};
        Projects.staticRun(data).then(staticSuccessFn, staticErrorFn);
      };

      function staticSuccessFn(data, status, headers, config) {
        Snackbar.show('Success!');
        $scope.text = data.data.output
        $scope.runningStatic = false;
      }

      function staticErrorFn(data, status, headers, config) {
        $scope.runningStatic = false;
      }

      $scope.runCancel = false;

      $scope.cancelRun = function () {
        $scope.runCancel = false;
        $scope.text = ["Execution cancelled."]
        Snackbar.show('Execution cancelled.');
      }

      $scope.runCode = function (){
        $scope.runCancel = true;
        $scope.text = []
        var data = {'id' : open_branches[$scope.selectedIndex].data.id,
                    'p_start': $scope.point_start,
                    'p_end': $scope.point_end
                  };
        Projects.run(data).then(runSuccessFn, runErrorFn);
      };

      $scope.stats_default = [['time', 'CPU', 'Core1', 'Core2', 'Core3', 'Core4', 'RAM', 'DISK'],
      ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']];
      $scope.stats = $scope.stats_default;
      $scope.total_cpu_usage = 'n/a';
      $scope.total_memory_usage = 'n/a';
      $scope.runtime = 'n/a';
      $scope.ret_points = ['n/a', 'n/a'];
      $scope.stats_interval = 1;
      StatsController($scope);
      $scope.update_stats();

      function runSuccessFn(data, status, headers, config) {
        Snackbar.show('Finished!');
        if($scope.runCancel){
          $scope.text = data.data.output;

          if(data.data.stats != undefined)
            $scope.stats = data.data.stats;
          else
            $scope.stats = $scope.stats_default;

          if($scope.pointset && data.data.points != undefined)
            $scope.ret_points = data.data.points;
          else
            $scope.ret_points = ['n/a', 'n/a'];

          if($scope.stats.length > 30){
            var tmp = $scope.stats.length%30;
            tmp = $scope.stats.length-tmp;
            $scope.stats_interval = tmp/30 + 1;
          }
          else
            $scope.stats_interval = 1;

          $scope.update_stats();
        }
        $scope.runCancel = false;
      }

      function runErrorFn(data, status, headers, config) {
        Snackbar.error('Run failed!');
        $scope.text = data.data.output;
        $scope.runCancel = false;
      }

      $scope.showAdvanced = function() {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: StatsController,
          templateUrl: 'stats.tmpl.html',
          clickOutsideToClose:true
        });
      };

      $scope.rename_dialog = function() {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'rename.tmpl.html',
          clickOutsideToClose:true
        })
      };

      $scope.rename = function(newName) {
        if($scope.selected_root){
          $scope.project.title = newName;
          Projects.update($scope.project).then(renameProjectSuccessFn, renameProjectErrorFn);

        }
        else{
          var name = newName + '.'  + open_branches[$scope.selectedIndex].data.f_type
          open_branches[$scope.selectedIndex].data.title = name;
          open_branches[$scope.selectedIndex].label = name;
          $scope.save_file();
        }

        $mdDialog.cancel();
      };

      function renameProjectSuccessFn(data, status, headers, config) {
        window.location = '/my-projects/' +  data.data.title;
      }

      function renameProjectErrorFn(data, status, headers, config) {
        Snackbar.error('Failed to rename project.');
      }

      $scope.pointset = false;
      $scope.point_start = 'start';
      $scope.point_end = 'end';

      $scope.insertPoints = function() {
        $mdDialog.show({
          scope: $scope.$new(),
          controller: DialogController,
          templateUrl: 'points.tmpl.html',
          clickOutsideToClose:true
        })
      };

      $scope.resetPoints = function() {
        $scope.pointset = false;
        $scope.tabs[$scope.selectedIndex].set_points = false;
        $scope.point_start = 'start';
        $scope.tabs[$scope.selectedIndex].point_start = 'start';
        $scope.point_end = 'end';
        $scope.tabs[$scope.selectedIndex].point_end = 'end';
        $mdDialog.cancel();
      };

      $scope.submitPoints = function(start, end) {
        if ((isNaN(start) && start != 'start') || parseInt(start) < 1)
          alert("Start point input must be the string 'start' or a number bigger than 0.");
        else {
          $scope.point_start = start;
          $scope.tabs[$scope.selectedIndex].point_start = start;
          if((isNaN(end) && end != 'end') || (!isNaN(start) && parseInt(start) >= parseInt(end)) || parseInt(end) < 2)
            alert("End point input must be the string 'end' or a number bigger than the start point.");
          else{
            $scope.point_end = end;
            $scope.tabs[$scope.selectedIndex].point_end = end;
            $scope.pointset = true;
            $scope.tabs[$scope.selectedIndex].set_points = true;
            if(start == 'start' && end == 'end')
              $scope.resetPoints();
            else
              $mdDialog.cancel();
          }
        }
      };

      $scope.stats_more_detail = function() {
        $scope.stats_interval = $scope.stats_interval - 1;
        $scope.update_stats();
      };

      $scope.stats_less_detail = function() {
        $scope.stats_interval = $scope.stats_interval + 1;
        $scope.update_stats();
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
        $scope.labels = ['Start'];
        $scope.series_cpu = ['CPU usage in nanoseconds'];
        $scope.data_cpu = [];
        $scope.cpu_usage = ['0'];
        $scope.points_line = ['0'];
        $scope.colors = ['#3498db'];

        if($scope.pointset){
          $scope.colors.push('#e74c3c');
          $scope.series_cpu = ['App usage', 'Set points usage'];
        }

        if($scope.stats.length > 2){
          for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval){
            $scope.labels.push(($scope.stats[i][0]) + ' sec');

            if(i == 1){
              $scope.cpu_usage.push(($scope.stats[1+$scope.stats_interval][1] - $scope.stats[$scope.stats_interval][1]) / 2);
              if($scope.pointset && $scope.ret_points[0] == 1)
                $scope.points_line.push(($scope.stats[1+$scope.stats_interval][1] - $scope.stats[$scope.stats_interval][1]) / 2);
              else
                $scope.points_line.push(0);
            }
            else{
              $scope.cpu_usage.push($scope.stats[i][1] - $scope.stats[i-1][1]);

              if($scope.pointset)
                if(i >= $scope.ret_points[0] && i <= $scope.ret_points[1])
                  $scope.points_line.push($scope.stats[i][1] - $scope.stats[i-1][1]);
                else
                  $scope.points_line.push('0');
            }
          }
        }

        $scope.labels.push('End');
        $scope.cpu_usage.push('0');
        $scope.data_cpu.push($scope.cpu_usage);

        if($scope.pointset){
          $scope.points_line.push('0');
          $scope.data_cpu.push($scope.points_line);
        }
      }

      $scope.getRAM = function(){
        /* RAM Usage */
        $scope.series_ram = ['RAM usage in kilobytes'];
        $scope.data_ram = [];
        $scope.ram_usage = ['0'];
        $scope.points_line = ['0'];
        $scope.colors = ['#3498db'];

        if($scope.pointset){
          $scope.colors.push('#e74c3c');
          $scope.series_ram = ['App usage', 'Set points usage'];
        }

        for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval){
          $scope.ram_usage.push(($scope.stats[i][6]/1000).toFixed(2));

          if($scope.pointset)
            if(i >= $scope.ret_points[0] && i <= $scope.ret_points[1])
              $scope.points_line.push(($scope.stats[i][6]/1000).toFixed(2));
            else
              $scope.points_line.push('0');
        }

        $scope.ram_usage.push('0');
        $scope.data_ram.push($scope.ram_usage);

        if($scope.pointset){
          $scope.points_line.push('0');
          $scope.data_ram.push($scope.points_line);
        }
      }

      $scope.getDiskIO = function(){
        /* DISK IO Usage */
        $scope.series_disk = ['DISK Memory usage in bytes'];
        $scope.data_disk = [];
        $scope.disk_io_usage = ['0'];
        $scope.points_line = ['0'];
        $scope.colors = ['#3498db'];

        if($scope.pointset){
          $scope.colors.push('#e74c3c');
          $scope.series_disk = ['App usage', 'Set points usage'];
        }

        for (var i = $scope.stats_interval; i < $scope.stats.length; i = i + $scope.stats_interval){
          $scope.disk_io_usage.push($scope.stats[i][7]);

          if($scope.pointset)
            if(i >= $scope.ret_points[0] && i <= $scope.ret_points[1])
              $scope.points_line.push($scope.stats[i][7]);
            else
              $scope.points_line.push('0');
        }

        $scope.disk_io_usage.push('0');
        $scope.data_disk.push($scope.disk_io_usage);

        if($scope.pointset){
          $scope.points_line.push('0');
          $scope.data_disk.push($scope.points_line);
        }
      }

      $scope.coreOvertime = function(){
        /* Core Usage */
          $scope.series_core = ['Core1', 'Core2', 'Core3', 'Core4'];
          $scope.data_core = [];
          $scope.core_line_options = {datasetFill : false}

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

        var totals_index = $scope.stats.length-1;
        $scope.data_core_total.push($scope.stats[totals_index][2]);
        $scope.data_core_total.push($scope.stats[totals_index][3]);
        $scope.data_core_total.push($scope.stats[totals_index][4]);
        $scope.data_core_total.push($scope.stats[totals_index][5]);
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

        $scope.getCpu();
        $scope.getRAM();
        $scope.getDiskIO();
        $scope.coreOvertime();
        $scope.getCore();
      }
    }
})();
