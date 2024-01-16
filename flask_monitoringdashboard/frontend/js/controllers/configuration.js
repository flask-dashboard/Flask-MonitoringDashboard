const HEADERS = {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
    }
}

export function ConfigurationController($scope, $http, menuService, endpointService, modalService) {
    endpointService.reset();
    menuService.reset('configuration');
    modalService.setConfirm('delete', () => deleteUser($scope.user));
    modalService.setConfirm('edit', () => editUser($scope.user));
    modalService.setConfirm('create', createUser);

    $scope.details = {};
    $scope.config = {};
    $scope.error = {};
    $scope.userData = [];

    $http.get('api/users').then(function (response) {
        $scope.userData = response.data;
    });

    $http.get('api/deploy_details').then(function (response) {
        $scope.details = response.data;
    });
    $http.get('api/deploy_config').then(function (response) {
        $scope.config = response.data;
    });

    $scope.openModal = function (name, user) {
        $scope.user = user;
        $(`#${name}Modal`).modal();
    }

    function fetchUsers() {
        $http.get('api/users').then(function (response) {
            $scope.userData = response.data;  // reload user data
        });
    }

    function createUser() {
        $http.post(
            'api/user/create',
            $.param({
                'username': $('#create-username')[0].value,
                'password': $('#create-pwd')[0].value,
                'password2': $('#create-pwd2')[0].value,
                'is_admin': $('#create-admin')[0].checked,
            }),
            HEADERS
        ).then(function (successResponse) {
            fetchUsers();
            $('#createModal').modal('hide');
            modalService.setErrorMessage('create', null); // remove error message.
        }, function (errorResponse) {
            modalService.setErrorMessage('create', errorResponse.data.message);
        });
    }

    function editUser() {
        $http.post(
            'api/user/edit',
            $.param({
                'user_id': $scope.user.id,
                'old_password': $('#edit-old-pwd')[0].value,
                'new_password': $('#edit-new-pwd')[0].value,
                'new_password2': $('#edit-new-pwd2')[0].value,
                'is_admin': $('#edit-admin')[0].checked,
            }),
            HEADERS
        ).then(function (successResponse) {
            fetchUsers();
            $('#editModal').modal('hide');
            modalService.setErrorMessage('edit', null); // remove error message.
        }, function (errorResponse) {
            modalService.setErrorMessage('edit', errorResponse.data.message);
        });
    }

    function deleteUser(user) {
        $http.post(
            'api/user/delete',
            $.param({
                'user_id': user.id
            }),
            HEADERS
        ).then(function (successResponse) {
            fetchUsers();
            $('#deleteModal').modal('hide');
            modalService.setErrorMessage('delete', null); // remove error message.
        }, function (errorResponse) {
            modalService.setErrorMessage('delete', errorResponse.data.message);
        });
    }

    $scope.telemetryConsent;

    $scope.fetchTelemetryConsent = function () {
        $http.get('/dashboard/telemetry/get_is_telemetry_answered')
            .then(function (response) {
                $scope.telemetryConsent = response.data.is_telemetry_answered.toString();;
            }, function (error) {
                console.error('Error fetching telemetry consent:', error);
            });
    };

    $scope.handleTelemetry = function (consent) {
        $http.post('/dashboard/telemetry/accept_telemetry_consent', { 'consent': consent })
            .then(function (response) {
            }, function (error) {
                console.error('Error updating telemetry consent:', error);
            });
    };

    $scope.fetchTelemetryConsent();

}