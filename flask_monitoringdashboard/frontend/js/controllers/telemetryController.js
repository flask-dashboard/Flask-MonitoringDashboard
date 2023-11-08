export function TelemetryController($scope, $http) {
    $scope.telemetryShow = true;
    $scope.followUpShow = false;

    $scope.acceptTelemetry = function() {
        $scope.telemetryShow = false;
        $http.post('/api/user/telemetry_consent', { consent: true })
            .then(function(response) {
                console.log('Consent recorded:', response.data);
            }, function(error) {
                console.error('Error recording consent:', error);
            });
    };

    $scope.declineTelemetry = function() {
        $scope.telemetryShow = false;
        $scope.followUpShow = true;
        $http.post('/api/user/telemetry_consent', { consent: false })
            .then(function(response) {
                console.log('Consent recorded:', response.data);
            }, function(error) {
                console.error('Error recording consent:', error);
            });
    };
}
