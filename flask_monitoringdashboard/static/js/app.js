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
        .when('/endpoint/:endpointId/hourly_load', {
            templateUrl: 'static/pages/plotly_graph.html',
            controller: EndpointHourlyLoadController
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
    this.page = '';
    this.name = '';
    this.showEndpoints = false;

    this.reset = function (page) {
        this.page = page;
        if (page == 'overview' || page == 'hourly_load' || page == 'multi_version' ||
            page == 'daily_load' || page == 'api_performance') {
            $('#collapseDashboard').collapse('show');
        } else {
            $('#collapseDashboard').collapse('hide');
        }

        if (page == 'endpoint_hourly' || page == 'endpoint_user_version' || page == 'endpoint_ip' ||
            page == 'endpoint_version' || page == 'endpoint_user' || page == 'endpoint_profiler' ||
            page == 'endpoint_grouped_profiler' || page == 'endpoint_outlier') {
            $('#collapseEndpoint').collapse('show');
        } else {
            $('#collapseEndpoint').collapse('hide');
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
    let that = this;

    this.dateFields = [];
    this.multiFields = [];

    this.clear = function () {
        that.multiFields = [];
        that.dateFields = [];
    };

    function addMultiSelect(name) {
        let obj = {
            'name': name,
            'values': [],
            'selected': [], // subset of 'items'
            'initialized': false
        };
        that.multiFields.push(obj);
        return obj;
    }

    this.initialize = function (obj) {
        obj.initialized = true;
        if (that.multiFields.every(o => o.initialized)) {
            that.reload();
        }
    };

    this.getMultiSelection = function (name) {
        return that.multiFields.find(o => o.name == name).selected;
    };

    this.addDate = function (name) {
        let obj = {
            'name': name,
            'value': new Date(),
        };
        that.dateFields.push(obj);
        return obj;
    };

    this.getDate = function (name) {
        return parseDate(that.dateFields.find(o => o.name == name).value);
    };

    this.addVersions = function () {
        let obj = addMultiSelect('versions');
        $http.get('api/versions').then(function (response) {
            obj.values = response.data;
            obj.selected = response.data.slice(-10);
            that.initialize(obj);
        });
    };

    this.addEndpoints = function () {
        let obj = addMultiSelect('endpoints');
        $http.get('api/endpoints').then(function (response) {
            obj.values = response.data.map(d => d.name);
            obj.selected = obj.values;
            that.initialize(obj);
        });
    };

    let parseDate = function (date) {
        return date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2)
            + "-" + ("0" + date.getDate()).slice(-2);
    };

    this.reload = function () {
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

app.service('endpointService', function ($http, $routeParams, menuService) {
    let that = this;
    this.info = {
        id: 0,
        name: ''
    };

    this.getInfo = function () {
        return this.info;
    };

    this.reset = function () {
        if (typeof $routeParams.endpointId !== 'undefined') {
            this.info.id = $routeParams.endpointId;
            this.getInfo();
        } else {
            this.info.id = 0;
            menuService.showEndpoints = false;
        }
    };

    this.onNameChanged = function (name) {
    };

    this.getInfo = function () {
        $http.get('api/endpoint_info/' + this.info.id).then(function (response) {
            that.info = response.data;
            console.log(that.info);
            that.info.name = response.data.endpoint;
            menuService.name = that.info.name;
            menuService.showEndpoints = true;
            that.onNameChanged(that.info.name);
        });
    };
});