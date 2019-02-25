function ConfigurationController($scope, $http, menuService, endpointService) {
    endpointService.reset();
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