export function ConfigurationController($scope, $http, menuService, endpointService, modalService) {
    endpointService.reset();
    menuService.reset('configuration');
    modalService.configure('Delete', 'Are you sure that you want to delete this user?')

    $scope.details = {};
    $scope.config = {};
    $scope.userData = [];

    $http.get('api/user_management').then(function (response) {
        $scope.userData = response.data;
    });

    $http.get('api/deploy_details').then(function (response) {
        $scope.details = response.data;
    });
    $http.get('api/deploy_config').then(function (response) {
        $scope.config = response.data;
    });

    $scope.deleteUser = function (user) {
        console.log(user);
        $http.post('api/user/delete',
            $.param({
                'user': user
            }),
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                }
            });
    };
}