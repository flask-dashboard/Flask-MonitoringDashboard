export function OutlierController($scope, $http, endpointService, menuService,
                           paginationService, plotlyService) {
    $scope.table = [];

    endpointService.reset();
    menuService.reset('endpoint_outlier');
    endpointService.onNameChanged = function (name) {
        $scope.title = 'Outliers for ' + name;
    };

    // Pagination
    paginationService.init('outliers');
    $http.get('api/num_outliers/' + endpointService.info.id).then(function (response) {
        paginationService.setTotal(response.data);
    });
    paginationService.onReload = function () {
        $http.get('api/outlier_table/' + endpointService.info.id + '/' +
            paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
        });
    };

    $http.get('api/outlier_graph/' + endpointService.info.id).then(function (response) {
        plotlyService.chart(response.data.map(row => {
            return {
                x: row.values,
                type: 'box',
                name: row.name,
                marker: {color: row.color}
            };
        }), {
            xaxis: {
                title: 'CPU loads (%)',
            },
            yaxis: {
                type: 'category',
                autorange: 'reversed'
            }
        });
    });
}