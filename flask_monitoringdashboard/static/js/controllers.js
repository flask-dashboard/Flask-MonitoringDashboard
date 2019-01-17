'use strict';

function OverviewController($scope, $http, $location, DTOptionsBuilder, menuService) {
    menuService.reset('overview');
    $scope.alertShow = false;
    $scope.pypi_version = '';
    $scope.dashboard_version = '';
    $scope.isHits = true;

    $scope.table = [];
    $scope.options = DTOptionsBuilder.newOptions().withOption('order', [[4, 'desc']]);

    $scope.selectedItem = 2;

    $scope.sendForm = function (row, value) {
        row.monitor = value;
        $http.post('api/set_rule',
            $.param({
                'name': row.name,
                'value': value
            }),
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                }
            });
    };

    $scope.toggleHits = function () {
        $scope.isHits = !$scope.isHits;
    };

    $http.get('api/overview').then(function (response) {
        $scope.table = response.data;
    });

    $scope.go = function (path) {
        $location.path(path);
    };

    $http.get('https://pypi.org/pypi/Flask-MonitoringDashboard/json').then(function (response) {
        $scope.pypi_version = response.data['info']['version'];

        $http.get('api/info').then(function (response) {
            $scope.dashboard_version = response.data['dashboard-version'];
            $scope.alertShow = $scope.pypi_version !== $scope.dashboard_version;
        })
    });
}

function ConfigurationController($scope, $http, menuService) {
    menuService.reset('configuration');

    $scope.details = {};
    $scope.config = {};

    $http.get('api/deploy_details').then(function (response) {
        $scope.details = response.data;
    });
    $http.get('api/deploy_config').then(function (response) {
        $scope.config = response.data;
    });
}

function HourlyLoadController($scope, $http, menuService, plotlyService, infoService, formService) {
    menuService.reset('hourly_load');

    // Set the information box
    infoService.axesText = 'The X-axis presents a number of days. The Y-axis presents every hour of the day.';
    infoService.contentText = 'The color of the cell presents the number of requests that the application ' +
        'received in a single hour. The darker the cell, the more requests it has processed. This information ' +
        'can be used to validate on which moment of the day the Flask application processes to most requests.';

    // Set the form handler
    $scope.handler = formService;
    $scope.handler.setForm('daterangeform');
    $scope.handler.setReload(function () {
        let start = $scope.handler.getStartDate();
        let end = $scope.handler.getEndDate();
        let times = [...Array(24).keys()].map(d => d + ":00");

        $http.get('api/hourly_load/' + start + '/' + end).then(function (response) {
            plotlyService.heatmap(response.data.days, times, response.data.data, {
                yaxis: {
                    autorange: 'reversed'
                }
            });
        });
    });
}

function MultiVersionController($scope, $http, menuService, formService, infoService, plotlyService) {
    menuService.reset('multi_version');

    // Set the information box
    infoService.axesText = 'The X-axis presents the versions that are used. The Y-axis presents the' +
        'endpoints that are found in the Flask application.';
    infoService.contentText = 'The color of the cell presents the distribution of the amount of requests ' +
        'that the application received in a single version for a single endpoint. The darker the cell, ' +
        'the more requests a certain endpoint has processed in that version. Since it displays the ' +
        'distribution of the load, each column sums up to 100%. This information can be used to validate ' +
        'which endpoints processes the most requests.';

    // Set the form handler
    $scope.handler = formService;
    $scope.handler.setForm('multiVersionsEndpoints');

    $scope.handler.setReload(function () {
        $http.post('api/multi_version', {
            data: {
                versions: $scope.handler.selectedVersions,
                endpoints: $scope.handler.selectedEndpoints
            }
        }).then(function (response) {
            plotlyService.heatmap($scope.handler.selectedVersions, $scope.handler.selectedEndpoints,
                response.data, {
                    xaxis: {
                        type: 'category',
                        title: 'Versions'
                    },
                    yaxis: {
                        type: 'category'
                    }
                });
        });
    });
}

function DailyUtilizationController($scope, $http, menuService, formService, infoService, plotlyService) {
    menuService.reset('daily_load');

    // Set the information box
    infoService.axesText = 'The X-axis presents the amount of requests. The Y-axis presents a number of days.';
    infoService.contentText = 'This graph presents a horizontal stacked barplot. Each endpoint is represented ' +
        'by a color. In the legend on the right, you can disable a certain endpoint by clicking on it. You can ' +
        'also show in the information of a single endpoint by double clicking that endpoint in the legend. The ' +
        'information from this graph can be used to see on which days (a subset of) the endpoints are used to most.';

    // Set the form handler
    $scope.handler = formService;
    $scope.handler.days_offset = 10;
    $scope.handler.setForm('daterangeform');
    $scope.handler.setReload(function () {
        let start = formService.getStartDate();
        let end = formService.getEndDate();

        $http.get('api/requests/' + start + '/' + end).then(function (response) {
            let data = response.data.data.map(obj => {
                return {
                    x: obj.values,
                    y: response.data.days,
                    name: obj.name,
                    type: 'bar',
                    orientation: 'h'
                };
            });

            plotlyService.chart(data, {
                barmode: 'stack',
                xaxis: {
                    title: 'Number of requests',
                },
                yaxis: {
                    type: 'category',
                    autorange: 'reversed'
                }
            });
        });
    });

    $scope.endpoints = [];

    $http.get('api/endpoints').then(function (response) {
        $scope.endpoints = response.data.map(d => d.name);
        $scope.handler.reload();
    });
}

function ApiPerformanceController($scope, $http, menuService, formService, infoService, plotlyService) {
    menuService.reset('api_performance');

    // Set the information box
    infoService.axesText = 'The X-axis presents the execution time in ms. The Y-axis presents every endpoint of ' +
        'the Flask application.';
    infoService.contentText = 'In this graph, it is easy to compare the execution time of the different endpoints ' +
        'across each other. This information can be used to validate which endpoints needs to be improved.';

    // Set the form handler
    $scope.handler = formService;
    $scope.handler.setForm('multiEndpoints');
    $scope.handler.setReload(function () {
        $http.post('api/api_performance', {
            data: {
                endpoints: $scope.handler.selectedEndpoints
            }
        }).then(function (response) {
            let data = response.data.map(obj => {
                return {
                    x: obj.values,
                    type: 'box',
                    name: obj.name,
                };
            });

            plotlyService.chart(data, {
                xaxis: {
                    title: 'Execution time (ms)',
                },
                yaxis: {
                    type: 'category'
                }
            });
        });
    });
}

function EndpointController($scope, $http, $routeParams, menuService) {
    menuService.setId($routeParams.endpointId);
}

app.controller('MenuController', function ($scope, menuService) {
    $scope.menu = menuService;
});

app.controller('InfoController', function ($scope, infoService) {
    $scope.info = infoService;
});