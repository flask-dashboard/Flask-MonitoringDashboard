export function SurveyController($scope, $http) {
    $scope.surveyShow = true;
    $scope.reasons = {
        privacy: false,
        performance: false,
        trust: false,
        other: false
    };

    $scope.submitFollowUp = function() {
        $scope.followUpShow = false;
        
        var feedback = [];
        for (var key in $scope.reasons) {
            if ($scope.reasons[key]) {
                feedback.push(key !== 'other' ? key : { other: $scope.customReason });
            }
        }
        
        $http.post('/api/feedback', { reasons: feedback })
            .then(function(response) {
                console.log('Feedback sent:', response.data);
            }, function(error) {
                console.error('Error sending feedback:', error);
            });
    };
}
