//Profile
(function () {
    'use strict';

    angular
        .module('pro1oh1.profiles.services')
        .factory('Profile', Profile);

    Profile.$inject = ['$http'];

    function Profile($http) {
        var Profile = {
            destroy: destroy,
            get: get,
            update: update
        };

        return Profile;

        //Destroy profile
        function destroy(username) {
            return $http.delete('/api/v1/accounts/' + username + '/');
        }

        //Get profile for user with given username
        function get(username) {
            return $http.get('/api/v1/accounts/' + username + '/');
        }

        //Update profile
        function update(profile) {
            return $http.put('/api/v1/accounts/' + profile.username + '/', profile);
        }
    }
})();
