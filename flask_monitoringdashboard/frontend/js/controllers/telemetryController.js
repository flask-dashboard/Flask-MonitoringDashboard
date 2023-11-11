export function TelemetryController($scope, $http) {
    $scope.telemetryShow = true;
    $scope.followUpShow = false;

    $scope.fetchConsent = function () {
        $http.post(`/dashboard/get_telemetry_answered`)
            .then(function (response) {
                $scope.telemetryShow = !response.data.get_telemetry_answered;
            }, function (error) {
                console.error('Error fetching consent:', error);
            });
    };
    $scope.fetchConsent();

    $scope.handleTelemetry = function (consent) {
        $scope.telemetryShow = false;
        $scope.followUpShow = !consent;

        $http.post('/dashboard/telemetry/accept_telemetry', { 'consent': consent })
            .then(function (response) {
                $scope.telemetryShow = false;
            }, function (error) {
                console.error('Error:', error);
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
                console.log('Feedback sent:', response.data);
            }, function (error) {
                console.error('Error sending feedback:', error);
            });
    };
}