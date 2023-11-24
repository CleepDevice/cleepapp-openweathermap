/**
 * OpenWeatherMap config directive
 * Handle openweathermap configuration
 */
angular
.module('Cleep')
.directive('openweathermapConfigComponent', ['toastService', 'openweathermapService', 'cleepService',
function(toast, openweathermapService, cleepService) {

    var openweathermapController = function() {
        var self = this;
        self.apikey = '';

        /**
         * Set api key
         */
        self.setApikey = function() {
            openweathermapService.setApikey(self.apikey)
                .then(function(resp) {
                    return cleepService.reloadModuleConfig('openweathermap');
                })
                .then(function(config) {
                    self.apikey = config.apikey;
                    toast.success('Configuration saved.');
                });
        };

        /**
         * Init controller
         */
        self.$onInit = function() {
            cleepService.getModuleConfig('openweathermap')
                .then(function(config) {
                    self.apikey = config.apikey;
                });
        };

    };

    return {
        templateUrl: 'openweathermap.config.html',
        replace: true,
        scope: true,
        controller: openweathermapController,
        controllerAs: '$ctrl',
    };
}]);

