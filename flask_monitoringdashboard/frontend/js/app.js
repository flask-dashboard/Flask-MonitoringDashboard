// Importing this font here will make it pass through the file loader, moving it to fonts/ directory
import "@fortawesome/fontawesome-free/webfonts/fa-solid-900.woff2"

// Plotly
import Plotly from 'plotly.js-cartesian-dist'

window.Plotly = Plotly;

// jQuery
import $ from 'jquery';

window.$ = window.jQuery = $;

// Popper.js
import { createPopper } from '@popperjs/core';


require('bootstrap');

// Moment
import moment from 'moment';

window.moment = moment;

import { OverviewController } from "./controllers/OverviewController";
import { HourlyLoadController } from "./controllers/hourlyLoad";
import { MultiVersionController } from "./controllers/multiVersion";
import { DailyUtilizationController } from "./controllers/dailyUtilization";
import { ApiPerformanceController } from "./controllers/apiPerformance";
import { ReportingController } from "./controllers/reporting";
import { EndpointHourlyLoadController } from "./controllers/endpointHourlyLoad";
import { EndpointVersionUserController } from './controllers/endpointVersionUser'
import { EndpointUsersController } from './controllers/endpointUsers'
import { EndpointProfilerController } from './controllers/endpointProfiler'
import { EndpointGroupedProfilerController } from './controllers/endpointGroupedProfiler'
import { OutlierController } from './controllers/endpointOutlier'
import { StatusCodeDistributionController, } from './controllers/statusCodeDistribution';
import { CustomGraphController } from './controllers/customGraph';
import { ConfigurationController } from './controllers/configuration';
import { DatabaseManagementController } from './controllers/databaseManagementController';
import { EndpointVersionIPController } from './controllers/endpointVersionIP';
import { EndpointVersionController } from "./controllers/endpointVersion";
import { MonitorLevelController } from "./controllers/monitorLevel";
import { TelemetryController } from "./controllers/telemetryController";


import formService from "./services/form";
import infoService from "./services/info";
import endpointService from "./services/endpoint";
import menuService from "./services/menu";
import paginationService from "./services/pagination";
import plotlyService from "./services/plotly";
import modalService from "./services/modal";
import {
    MenuController,
    InfoController,
    EndpointController,
    FormController,
    PaginationController,
    ModalController,
} from './controllers/util';
import { applyFilters } from "./filters";
import applyDirectives from "./directives";

let app = angular.module('fmdApp', ['ngRoute']);
applyFilters(app);
applyDirectives(app);

app.service('formService', ['$http', 'endpointService', '$filter', formService]);
app.service('infoService', infoService);
app.service('endpointService', ['$http', '$routeParams', endpointService]);
app.service('menuService', ['$http', 'endpointService', menuService]);
app.service('paginationService', ['$http', 'endpointService', menuService]);
app.service('paginationService', paginationService);
app.service('plotlyService', ['formService', plotlyService]);
app.service('modalService', modalService);

app.controller('MonitorLevelController', ['$scope', '$http', MonitorLevelController]);

app.controller('MenuController', ['$scope', 'menuService', MenuController]);
app.controller('InfoController', ['$scope', 'infoService', InfoController]);
app.controller('FormController', ['$scope', 'formService', FormController]);
app.controller('EndpointController', ['$scope', 'endpointService', EndpointController]);
app.controller('PaginationController', ['$scope', 'paginationService', PaginationController]);
app.controller('ModalController', ['$scope', '$window', '$browser', 'modalService', ModalController]);

app.component('telemetryComponent', {
    templateUrl: 'static/pages/telemetry.html',
    controller: TelemetryController
});

app.config(['$locationProvider', '$routeProvider', function ($locationProvider, $routeProvider) {
    $routeProvider
        .when('/overview', {
            templateUrl: 'static/pages/overview.html',
            controller: ['$scope', '$http', '$location', 'menuService', 'endpointService', OverviewController]
        })
        .when('/hourly_load', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'menuService', 'plotlyService', 'infoService',
                'formService', 'endpointService', '$filter', HourlyLoadController]
        })
        .when('/multi_version', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'menuService', 'formService', 'infoService', 'plotlyService', 'endpointService', MultiVersionController]
        })
        .when('/daily_utilization', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'menuService', 'formService', 'infoService',
                'plotlyService', 'endpointService', DailyUtilizationController]
        })
        .when('/api_performance', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'menuService', 'formService', 'infoService',
                'plotlyService', 'endpointService', ApiPerformanceController]
        })
        .when('/reporting', {
            templateUrl: 'static/pages/reporting.html',
            controller: ['$scope', '$http', 'menuService', 'endpointService', 'plotlyService', ReportingController]
        })
        .when('/endpoint/:endpointId/hourly_load', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'menuService', 'endpointService',
                'infoService', 'formService', 'plotlyService', '$filter', EndpointHourlyLoadController]
        })
        .when('/endpoint/:endpointId/version_user', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: [
                '$scope', '$http', 'infoService', 'endpointService',
                'menuService', 'formService', 'plotlyService', '$filter', EndpointVersionUserController]
        })
        .when('/endpoint/:endpointId/version_ip', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: [
                '$scope', '$http', 'infoService', 'endpointService',
                'menuService', 'formService', 'plotlyService', '$filter', EndpointVersionIPController]
        })
        .when('/endpoint/:endpointId/versions', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'infoService', 'endpointService',
                'menuService', 'formService', 'plotlyService', '$filter', EndpointVersionController]
        })
        .when('/endpoint/:endpointId/users', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'infoService', 'endpointService',
                'menuService', 'formService', 'plotlyService', EndpointUsersController]
        })
        .when('/endpoint/:endpointId/profiler', {
            templateUrl: 'static/pages/profiler.html',
            controller: ['$scope', '$http', 'menuService', 'endpointService',
                'paginationService', 'formService', EndpointProfilerController]
        })
        .when('/endpoint/:endpointId/grouped-profiler', {
            templateUrl: 'static/pages/grouped_profiler.html',
            controller: ['$scope', '$http', 'menuService',
                'endpointService', 'formService', EndpointGroupedProfilerController]
        })
        .when('/endpoint/:endpointId/outliers', {
            templateUrl: 'static/pages/outliers.html',
            controller: ['$scope', '$http', 'endpointService', 'menuService',
                'paginationService', 'plotlyService', OutlierController]
        })
        .when('/endpoint/:endpointId/status_code_distribution', {
            templateUrl: 'static/pages/status_code_distribution.html',
            controller: [
                '$scope', '$http', 'infoService', 'endpointService', 'menuService', 'formService', 'plotlyService', StatusCodeDistributionController],
        })
        .when('/custom_graph/:graphId', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: ['$scope', '$http', 'infoService', 'endpointService',
                'menuService', 'formService', 'plotlyService', CustomGraphController]
        })
        .when('/configuration', {
            templateUrl: 'static/pages/configuration.html',
            controller: ['$scope', '$http', 'menuService', 'endpointService', 'modalService', ConfigurationController]
        })
        .when('/database_management', {
            templateUrl: 'static/pages/database_management.html',
            controller: ['$scope', '$http', 'menuService', 'endpointService', 'modalService', DatabaseManagementController]
        })
        .otherwise({
            redirectTo: '/overview'
        });

    $locationProvider.html5Mode({
        enabled: true,
        requireBase: true
    });
}]);

// Toggle the side navigation
$("#sidenavToggler").click(function (e) {
    e.preventDefault();
    $("body").toggleClass("sidenav-toggled");
    $(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
    $(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
});
// Force the toggled class to be removed when a collapsible nav link is clicked
$(".navbar-sidenav .nav-link-collapse").click(function (e) {
    e.preventDefault();
    $("body").removeClass("sidenav-toggled");
});


window.app = app;