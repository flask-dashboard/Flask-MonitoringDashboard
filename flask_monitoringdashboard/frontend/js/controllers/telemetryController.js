export function TelemetryController($scope, $http) {
    $scope.telemetryShow = true;
    $scope.followUpShow = false;

    $scope.fetchTelemetryConsent = function () {
        $http.get(`/dashboard/telemetry/get_is_telemetry_answered`)
            .then(function (response) {
                $scope.telemetryShow = !response.data.is_telemetry_answered;
            }, function (error) {
                console.error('Error fetching telemetry consent:', error);
            });
    };
    $scope.fetchTelemetryConsent();

    $scope.handleTelemetry = function (consent) {
        $scope.telemetryShow = false;
        $scope.followUpShow = !consent;

        $http.post('/dashboard/telemetry/accept_telemetry_consent', { 'consent': consent })
            .then(function (response) {
                $scope.telemetryShow = false;
            }, function (error) {
                console.error('Error updating telemetry consent:', error);
            });
    };


    $scope.reasons = {
        privacy: false,
        performance: false,
        trust: false,
        other: false
    };
    $scope.customReason = '';

    var config = {
        headers: {
            'X-Parse-Application-Id': '',
            'X-Parse-REST-API-Key': '',
            'Content-Type': 'application/json'
        }
    };

    $scope.submitFollowUp = function () {
        $scope.followUpShow = false;

        var feedback = [];
        for (var key in $scope.reasons) {
            if ($scope.reasons[key]) {
                if (key === 'other') {
                    feedback.push(key);
                    if ($scope.customReason.trim() !== '') {
                        feedback.push({ other: $scope.customReason });
                    }
                } else {
                    feedback.push(key);
                }
            }
        }
        $http.post('https://parseapi.back4app.com/classes/FollowUp', { reasons: feedback }, config)
            .then(function (response) {
            }, function (error) {
                console.error('Error sending feedback:', error);
            });
    };
}