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
            $scope.alertShow = !isNewestVersion($scope.pypi_version, $scope.dashboard_version);
        })
    });


}

function isNewestVersion(pypi_version, dashboard_version ){
    let pypi_version_array = pypi_version.split('.');
    let dashboard_version_array = dashboard_version.split('.');
    for(let i=0; i<3; i++){
        if (pypi_version_array[i] > dashboard_version_array[i]){
            return false;
        }
    }
    return true;
}
