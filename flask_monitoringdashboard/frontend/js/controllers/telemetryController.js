export function TelemetryController($scope, $http, $window) {

    // Check if telemetry response is already stored in local storage
    const telemetryAnswered = $window.localStorage.getItem('telemetryAnswered') === 'true';

    // Control the visibility of the telemetry prompt based on previous response
    $scope.telemetryShow = !telemetryAnswered;
    $scope.followUpShow = false;

    // Function to fetch telemetry consent status from database 
    $scope.fetchTelemetryConsent = function () {
        $http.get(`/dashboard/telemetry/get_is_telemetry_answered`)
            .then(function (response) {
                $scope.telemetryShow = !response.data.is_telemetry_answered;
            }, function (error) {
                console.error('Error fetching telemetry consent:', error);
            });
    };
    $scope.fetchTelemetryConsent();

    // Function to handle user response to telemetry prompt
    $scope.handleTelemetry = function (consent) {
        $scope.telemetryShow = false;
        $scope.followUpShow = !consent;

        $http.post('/dashboard/telemetry/accept_telemetry_consent', { 'consent': consent })
            .then(function (response) {
                $scope.telemetryShow = false;
                $window.localStorage.setItem('telemetryAnswered', 'true');
            }, function (error) {
                console.error('Error updating telemetry consent:', error);
            });
    };

    // Object to track reasons for declining telemetry
    $scope.reasons = {
        privacy: false,
        performance: false,
        trust: false,
        other: false
    };
    $scope.customReason = '';

    // Function to submit follow-up feedback
    $scope.submitFollowUp = function () {
        $scope.followUpShow = false;
    
        var feedback = [];
        for (var key in $scope.reasons) {
            if ($scope.reasons[key]) {
                if (key === 'other' && $scope.customReason.trim() !== '') {
                    feedback.push({ key: 'other', other_reason: $scope.customReason });
                } else {
                    feedback.push({ key: key });
                }
            }
        }
    
        $http.post('/dashboard/telemetry/submit_follow_up', { feedback: feedback })
            .then(function (response) {
            }, function (error) {
                console.error('Error sending feedback:', error);
            });
    };
}