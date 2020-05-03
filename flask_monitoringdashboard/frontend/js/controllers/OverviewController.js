export function OverviewController($scope, $http, $location, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('overview');
    $scope.alertShow = false;
    $scope.pypi_version = '';
    $scope.dashboard_version = '';
    $scope.isHits = true;

    $scope.table = [];
    $scope.selectedItem = 2;

    $scope.searchQuery = '';
    $scope.pageSize = '10';
    $scope.currentPage = 0;

    $scope.toggleHits = function () {
        $scope.isHits = !$scope.isHits;
    };

    $http.get('api/overview').then(function (response) {
        $scope.table = response.data;
    });

    $scope.getFilteredItems = function () {
        const start = Number($scope.currentPage) * $scope.pageSize;
        const end = (Number($scope.currentPage) + 1) * Number($scope.pageSize);

        return $scope.table
            .filter(item => item.name.includes($scope.searchQuery))
            .slice(start, end);
    }

    $scope.canGoBack = function () {
        console.log('hello', $scope.currentPage);

        return $scope.currentPage > 0;
    }

    $scope.canGoForward = function () {
        const start = Number($scope.currentPage + 1) * $scope.pageSize;
        const end = (Number($scope.currentPage + 1) + 1) * Number($scope.pageSize);

        const data = $scope.table
            .filter(item => item.name.includes($scope.searchQuery))
            .slice(start, end);

        console.log(data);

        return data.length > 0;
    }

    $scope.nextPage = function () {
        $scope.currentPage++;
    }

    $scope.previousPage = function () {
        $scope.currentPage--;
    }


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

function isNewestVersion(pypi_version, dashboard_version) {
    let pypi_version_array = pypi_version.split('.');
    let dashboard_version_array = dashboard_version.split('.');
    for (let i = 0; i < 3; i++) {
        if (pypi_version_array[i] > dashboard_version_array[i]) {
            return false;
        }
    }
    return true;
}
