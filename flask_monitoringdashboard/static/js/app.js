'use strict';

let app = angular.module('fmdApp', ['ngRoute', 'datatables']);

app.config(function ($locationProvider, $routeProvider) {

    $routeProvider
        .when('/overview', {
            templateUrl: 'static/pages/overview.html',
            controller: OverviewController
        })
        .when('/hourly_load', {
            templateUrl: 'static/pages/hourly_load.html',
            controller: HourlyLoadController
        })
        .when('/multi_version', {
            templateUrl: 'static/pages/multi_version.html',
            controller: MultiVersionController
        })
        .when('/daily_utilization', {
            templateUrl: 'static/pages/daily_utilization.html',
            controller: DailyUtilizationController
        })
        .when('/endpoint/:endpointId', {
            templateUrl: 'static/pages/page1.html',
            controller: EndpointController
        })
        .when('/configuration', {
            templateUrl: 'static/pages/configuration.html',
            controller: ConfigurationController
        })
        .otherwise({
            redirectTo: '/overview'
        });

    $locationProvider.html5Mode({
        enabled: true,
        requireBase: true
    });
});

app.service('menuHelper', function($http){
    this.id = 0;
    this.name = '';
    this.isset = false;
    let that = this;

    this.set = function(id, name){
        this.id = id;
        this.name = name;
        this.isset = true;
    };

    this.setId = function(id){
        $http.get('api/endpoint_info/' + id).then(function(response){
            let name = response.data.endpoint;
            that.set(id, name);
        })
    };

    this.reset = function(){
        this.isset = false;
    }
});