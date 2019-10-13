'use strict';

let app = angular.module('fmdApp', ['ngRoute', 'datatables']);

app.config(function ($locationProvider, $routeProvider) {

    $routeProvider
        .when('/overview', {
            templateUrl: 'static/pages/overview.html',
            controller: OverviewController
        })
        .when('/hourly_load', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: HourlyLoadController
        })
        .when('/multi_version', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: MultiVersionController
        })
        .when('/daily_utilization', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: DailyUtilizationController
        })
        .when('/api_performance', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ApiPerformanceController
        })
        .when('/reporting', {
            templateUrl: 'static/pages/reporting.html',
            controller: ReportingController
        })
        .when('/endpoint/:endpointId/hourly_load', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: EndpointHourlyLoadController
        })
        .when('/endpoint/:endpointId/version_user', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: EndpointVersionUserController
        })
        .when('/endpoint/:endpointId/version_ip', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: EndpointVersionIPController
        })
        .when('/endpoint/:endpointId/versions', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: EndpointVersionController
        })
        .when('/endpoint/:endpointId/users', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: EndpointUsersController
        })
        .when('/endpoint/:endpointId/profiler', {
            templateUrl: 'static/pages/profiler.html',
            controller: EndpointProfilerController
        })
        .when('/endpoint/:endpointId/grouped-profiler', {
            templateUrl: 'static/pages/grouped_profiler.html',
            controller: EndpointGroupedProfilerController
        })
        .when('/endpoint/:endpointId/outliers', {
            templateUrl: 'static/pages/outliers.html',
            controller: OutlierController
        })
        .when('/endpoint/:endpointId/status_code_distribution', {
            templateUrl: 'static/pages/status_code_distribution.html',
            controller: StatusCodeDistributionController,
        })
        .when('/custom_graph/:graphId', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: CustomGraphController
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