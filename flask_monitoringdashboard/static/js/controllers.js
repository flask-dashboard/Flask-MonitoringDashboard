'use strict';

function OverviewController($scope, $http, $location, DTOptionsBuilder, menuHelper) {
    menuHelper.reset();
    $scope.alertShow = false;
    $scope.pypi_version = '';
    $scope.dashboard_version = '';
    $scope.isHits = true;

    $scope.table = [];
    $scope.options = DTOptionsBuilder.newOptions().withOption('order', [[4, 'desc']]);

    $scope.selectedItem = 2;

    $scope.compare = function (level, n) {
        return (level == n);
    };

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

function ConfigurationController($scope, $http, menuHelper) {
    menuHelper.reset();

    $scope.details = {};
    $scope.config = {};

    $http.get('api/deploy_details').then(function (response) {
        $scope.details = response.data;
    });
    $http.get('api/deploy_config').then(function (response) {
        $scope.config = response.data;
    });
}

function HourlyLoadController($scope, $http, menuHelper) {
    menuHelper.reset();

    $scope.endDate = new Date();
    $scope.startDate = new Date();
    $scope.startDate.setDate($scope.startDate.getDate() - 14);
    $scope.data = [];

    let parseDate = function (date) {
        return date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2)
            + "-" + ("0" + date.getDate()).slice(-2);
    };

    $scope.refresh = function () {
        let start = parseDate($scope.startDate);
        let end = parseDate($scope.endDate);
        let times = [...Array(24).keys()].map(d => d + ":00");

        $http.get('api/hourly_load/' + start + '/' + end).then(function (response) {

            Plotly.newPlot('chart', [{
                x: response.data.days,
                y: times,
                z: response.data.data,
                type: 'heatmap'
            }], {
                height: 600,
                yaxis: {
                    autorange: 'reversed'
                }
            }, {
                displaylogo: false,
                responsive: true
            });
        });
    };

    $scope.refresh();
}

function MultiVersionController($scope, $http, menuHelper) {
    menuHelper.reset();
    $scope.versions = [];
    $scope.selectedVersions = $scope.versions;
    $scope.endpoints = [];
    $scope.selectedEndpoints = [];

    $http.get('api/versions').then(function (response) {
        $scope.versions = response.data;
        $scope.selectedVersions = $scope.versions.slice(-10);

        $http.get('api/endpoints').then(function (response) {
            $scope.endpoints = response.data.map(d => d.name);
            $scope.selectedEndpoints = $scope.endpoints;

            $scope.refresh();
        })
    });

    $scope.refresh = function () {
        $http.post('api/multi_version', {
            data: {
                versions: $scope.selectedVersions,
                endpoints: $scope.selectedEndpoints
            }
        }).then(function (response) {
            Plotly.newPlot('chart', [{
                x: $scope.selectedVersions,
                y: $scope.selectedEndpoints,
                z: response.data,
                type: 'heatmap'
            }], {
                height: 600,
                xaxis: {
                    type: 'category',
                    title: 'Versions'
                },
                yaxis: {
                    type: 'category'
                }
            }, {
                displaylogo: false,
                responsive: true
            });
        });
    }
}


function EndpointController($scope, $http, $routeParams, menuHelper) {
    menuHelper.setId($routeParams.endpointId);
}

app.controller('MenuController', function ($scope, menuHelper) {
    $scope.menu = menuHelper;
});