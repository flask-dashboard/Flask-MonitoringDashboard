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

app.service('menuService', function ($http) {
    this.id = 0;
    this.page = '';
    this.name = '';
    this.isset = false;
    let that = this;

    this.set = function (id, name) {
        this.id = id;
        this.name = name;
        this.isset = true;
    };

    this.setId = function (id) {
        $http.get('api/endpoint_info/' + id).then(function (response) {
            let name = response.data.endpoint;
            that.set(id, name);
        })
    };

    this.reset = function (page) {
        this.page = page;
        this.isset = false;
        if (page == 'overview' || page == 'hourly_load' || page == 'multi_version' ||
            page == 'daily_load' || page == 'api_performance') {
            $('#collapseDashboard').collapse('show');
        } else {
            $('#collapseDashboard').collapse('hide');
        }
    }
});

app.service('plotlyService', function () {
    let layout = {
        height: 600,
    };
    let options = {
        displaylogo: false,
        responsive: true
    };

    this.heatmap = function (x, y, z, layout_ext) {
        this.chart([{
            x: x,
            y: y,
            z: z,
            type: 'heatmap'
        }], layout_ext);
    };

    this.chart = function (data, layout_ext) {
        Plotly.newPlot('chart', data, $.extend({}, layout, layout_ext), options);
    }
});

app.service('formService', function ($http) {

    // Form variables
    // - daterangeform
    this.endDate = new Date();
    this.startDate = new Date();

    // - multiVersionsEndpoints
    // - multiEndpoints (only 3rd and 4th)
    this.versions = [];
    this.selectedVersions = this.versions;
    this.endpoints = [];
    this.selectedEndpoints = [];

    // Service variables
    this.form = '';
    this.days_offset = 14;
    let that = this;

    this.setForm = function (formType) {
        that.form = formType;
        if (formType == 'multiVersionsEndpoints') {
            $http.get('api/versions').then(function (response) {
                that.versions = response.data;
                that.selectedVersions = that.versions.slice(-10);
                getEndpointNames();
            });
        } else if (formType == 'daterangeform') {
            that.startDate.setDate(that.startDate.getDate() - that.days_offset);
            that.reload();
        } else { // formType == 'multiEndpoints'
            getEndpointNames();
        }
    };

    function getEndpointNames() {
        $http.get('api/endpoints').then(function (response) {
            that.endpoints = response.data.map(d => d.name);
            that.selectedEndpoints = that.endpoints;
            that.reload();
        });
    };

    let parseDate = function (date) {
        return date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2)
            + "-" + ("0" + date.getDate()).slice(-2);
    };


    this.reload = function () {
    };

    this.getStartDate = function () {
        return parseDate(this.startDate);
    };

    this.getEndDate = function () {
        return parseDate(this.endDate);
    };
    this.setReload = function (f) {
        this.reload = f;
    }
});

app.service('infoService', function () {
    this.graphText = 'You can hover the graph with your mouse to see the actual values. You can also use the ' +
        'buttons at the top of the graph to select a subset of graph, scale it accordingly or save the graph ' +
        'as a PNG image.';
    this.axesText = '';
    this.contentText = '';
});