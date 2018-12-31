'use strict';

function OverviewController($scope, $http, $location, NgTableParams) {
    $scope.alert_show = false;
    $scope.pypi_version = '';
    $scope.dashboard_version = '';
    $scope.title = 'Dashboard Overview';

    $scope.tableParams = new NgTableParams({
        page: 1,
        count: 10
    }, {
        getData: function (params) {
            /* code to fetch data that matches the params values EG: */
            return $http.get('api/overview').then(function (response) {
                params.total(response.data.length);
                return response.data;
            });
        }
    });

    $scope.go = function (path) {
        $location.path(path);
    };


    $http.get('https://pypi.org/pypi/Flask-MonitoringDashboard/json').then(function (response) {
        $scope.pypi_version = response.data['info']['version'];

        $http.get('api/info').then(function (response) {
            $scope.dashboard_version = response.data['dashboard-version'];
            $scope.alert_show = $scope.pypi_version !== $scope.dashboard_version;
        })
    });
}

function EndpointController($scope, $http, $routeParams) {
    console.log($routeParams.endpointId);
}