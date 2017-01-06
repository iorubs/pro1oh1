//Snackbar
(function ($, _) {
    'use strict';

    angular
        .module('pro1oh1.utils.services')
        .factory('Snackbar', Snackbar);

    function Snackbar() {
        var Snackbar = {
            error: error,
            show: show
        };

        return Snackbar;

        //Display a snackbar
        function _snackbar(content, options) {
            options = _.extend({ timeout: 3000 }, options);
            options.content = content;

            $.snackbar(options);
        }

        //Display an error snackbar
        function error(content, options) {
            _snackbar('Error: ' + content, options);
        }

        //Display a standard snackbar
        function show(content, options) {
            _snackbar(content, options);
        }
    }
})($, _);