export function ExceptionController($scope, $http, menuService, paginationService, endpointService) {
    endpointService.reset();
    menuService.reset('exception_overview'); 

    $scope.table = [];

    paginationService.init('exceptions');
    $http.get('api/num_exceptions').then(function (response) {
        paginationService.setTotal(response.data);
    });

    paginationService.onReload = function () {
        $http.get('api/exception_info/' + paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
        });
    };
};
