/**
 * OpenWeatherMap service
 * Handle openweathermap module requests
 */
angular
.module('Cleep')
.service('openweathermapService', ['rpcService', function(rpcService) {
    var self = this;

    self.setApikey = function(apikey) {
        return rpcService.sendCommand('set_apikey', 'openweathermap', {'apikey':apikey});
    };

    self.getWeather = function() {
        return rpcService.sendCommand('get_weather', 'openweathermap', {});
    };

    self.getForecast = function() {
        return rpcService.sendCommand('get_forecast', 'openweathermap', {});
    };

}]);

