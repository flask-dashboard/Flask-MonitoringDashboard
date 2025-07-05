export function OverviewController($scope, $http, $location, menuService, paginationService, endpointService) {
    endpointService.reset();
    menuService.reset('overview');
    paginationService.init('endpoints');

    $scope.alertShow = false;
    $scope.pypi_version = '';
    $scope.dashboard_version = '';
    $scope.isHits = true;

    $scope.sortBy = 'name';
    $scope.isDesc = true;

    $scope.table = [];
    $scope.selectedItem = 2;

    $scope.searchQuery = '';
    $scope.pageSize = '10';
    $scope.blueprints = [''];
    $scope.slectedBlueprint = '';

    $scope.toggleHits = function () {
        $scope.isHits = !$scope.isHits;
    };

    $http.get('api/overview').then(function (response) {
        response.data.forEach((endpoint) => {
            if (!$scope.blueprints.includes(endpoint.blueprint)) {
                $scope.blueprints.push(endpoint.blueprint);
            }
        })
        $scope.table = response.data;
        paginationService.setTotal(response.data.length);
    });

    function ascendingOrder(a, b){
        if ($scope.sortBy === 'last-accessed') {
            return (Date.parse(a[$scope.sortBy]) || null) - (Date.parse(b[$scope.sortBy]) || null);
        }

        return a[$scope.sortBy] - b[$scope.sortBy];
    }

    function descendingOrder(a, b){
        return ascendingOrder(b, a);
    }
    
    function sortItems(items){
      return $scope.isDesc ? items.sort(descendingOrder) : items.sort(ascendingOrder)
    }

    $scope.getFilteredItemsForPage = function () {
        paginationService.perPage = Number($scope.pageSize);
        var pageNumber = paginationService.page;
        var pageSize = paginationService.perPage;
        const start = (pageNumber - 1)* pageSize;
        const end = pageNumber * pageSize;
  
        let items = $scope.table
            .filter(item => item.name.includes($scope.searchQuery));

        if ($scope.slectedBlueprint) {
            items = items.filter(item => item.blueprint===$scope.slectedBlueprint);
        }
    
        return sortItems(items).slice(start, end);
    }

    $scope.changeSortingOrder = function (column) {
        if (column !== $scope.sortBy){
            $scope.isDesc = true;
            $scope.sortBy = column;
            return;
        }
        $scope.isDesc = !$scope.isDesc;
    }

    $scope.getSortArrowClassName = function (column) {
      return {
        'rotate-up': !$scope.isDesc && $scope.sortBy === column,
        'rotate-down': $scope.isDesc && $scope.sortBy === column,
        'text-gray': $scope.sortBy !== column 
      }
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
            return false;  // using an older version.
        } else if (pypi_version_array[i] < dashboard_version_array[i]){
            return true;  // using a newer version.
        }
    }
    return true;  // using the same version.
}
