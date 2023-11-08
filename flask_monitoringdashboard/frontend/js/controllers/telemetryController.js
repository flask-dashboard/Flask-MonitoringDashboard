export function TelemetryController($scope, $http) {
    $scope.telemetryShow = true;
    $scope.followUpShow = false;

    var config = {
        headers: {
            'X-Parse-Application-Id': '',
            'X-Parse-REST-API-Key': '', 
            'Content-Type': 'application/json'
        }
    };

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

     $scope.submitFollowUp = function() {
        $scope.followUpShow = false;
        
        var feedback = [];
        for (var key in $scope.reasons) {
            if ($scope.reasons[key]) {
                feedback.push(key !== 'other' ? key : { other: $scope.customReason });
            }
        }
        
        // Setup the data to be sent
        var data = {
            reasons: feedback
        };

        // Perform the POST request to the Back4App server
        $http.post('https://parseapi.back4app.com/classes/Feedback1', data, config)
            .then(function(response) {
                console.log('Feedback sent:', response.data);
            }, function(error) {
                console.error('Error sending feedback:', error);
            });
    };
}
