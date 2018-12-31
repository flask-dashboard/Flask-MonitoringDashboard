'use strict';

let app = angular.module('fmdApp', ['ngRoute', 'ngTable']);

app.config(function ($locationProvider, $routeProvider) {

    $routeProvider
        .when('/', {
            templateUrl: 'static/pages/overview.html',
            controller: OverviewController
        })
        .when('/endpoint/:endpointId', {
            templateUrl: 'static/pages/page1.html',
            controller: EndpointController
        })
        .otherwise({
            redirectTo: '/'
        });

    $locationProvider.html5Mode({
        enabled: true,
        requireBase: true
    });
});