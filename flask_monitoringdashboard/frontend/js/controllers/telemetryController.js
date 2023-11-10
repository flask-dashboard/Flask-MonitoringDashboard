export function TelemetryController($scope, $http) {
    $scope.telemetryShow = false;
    $scope.followUpShow = false;

    $scope.UUID = 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'

    $scope.reasons = {
        privacy: false,
        performance: false,
        trust: false,
        other: false
    };

    var config = {
        headers: {
            'X-Parse-Application-Id': '',
            'X-Parse-REST-API-Key': '',
            'Content-Type': 'application/json'
        }
    };

    $scope.fetchConsent = function () {
        var queryParams = {
            UUID: $scope.UUID
        };
    
        var queryString = encodeURIComponent(JSON.stringify(queryParams));
    
        $http.get(`https://parseapi.back4app.com/classes/Test1?where=${queryString}`, config)
            .then(function (response) {
                if (response.data.results.length === 0) {
                    $scope.telemetryShow = true
                }
            }, function (error) {
                console.error('Error fetching consent:', error);
            });
    };
    
    $scope.fetchConsent();

    $scope.handleTelemetry = function (consent) {
        $scope.telemetryShow = false;
        $scope.followUpShow = !consent;

        $http.post('https://parseapi.back4app.com/classes/Test1', { UUID: $scope.UUID, consent: consent }, config)
            .then(function (response) {
                console.log('Consent recorded:', response.data);
            }, function (error) {
                console.error('Error recording consent:', error);
            });
    };

    $scope.submitFollowUp = function () {
        $scope.followUpShow = false;

        var feedback = [];
        for (var key in $scope.reasons) {
            if ($scope.reasons[key]) {
                feedback.push(key !== 'other' ? key : { other: $scope.customReason });
            }
        }

        $http.post('https://parseapi.back4app.com/classes/Test1', { UUID: $scope.UUID, reasons: feedback }, config)
            .then(function (response) {
                console.log('Feedback sent:', response.data);
            }, function (error) {
                console.error('Error sending feedback:', error);
            });
    };
}