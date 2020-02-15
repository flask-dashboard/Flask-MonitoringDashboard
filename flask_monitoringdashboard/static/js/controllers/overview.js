function OverviewController($scope, $http, $location, DTOptionsBuilder, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('overview');
    $scope.alertShow = false;
    $scope.pypi_version = '';
    $scope.dashboard_version = '';
    $scope.isHits = true;

    $scope.table = [];
    $scope.options = DTOptionsBuilder.newOptions().withOption('order', [[4, 'desc']]);

    $scope.selectedItem = 2;

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

        $http.get('api/deploy_details').then(function (response) {
            $scope.dashboard_version = response.data['dashboard-version'];
            $scope.alertShow = !(isNewestVersion($scope.pypi_version,$scope.dashboard_version))
        })
    });


}

function isNewestVersion(pypi_version,dashboard_version ){ // greater than or equal
    if (pypi_version[0] > dashboard_version[0]) return false;
    else if (pypi_version[2] > dashboard_version[2]) return false;
    else if (pypi_version[4] > dashboard_version[4]) return false;
    else true;
}
