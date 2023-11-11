export function SurveyController($scope, $http) {
    $scope.surveyShow = false;
    $scope.surveyCompleted = false; // New flag for survey completion
    $scope.surveyVariationIndex = 0;
    $scope.surveyVariations = [
        'Please take a moment to <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">fill out our survey</a>.',
        'Your feedback is valuable! <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">Take our quick survey.</a>',
        'We value your opinion! Click <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">here</a> to share your thoughts.',
        'Help us improve! Participate in our <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">short survey</a>.'
    ];
    

    $scope.fetchSurveyStatus = function () {
        $http.post('/dashboard/survey_status')
            .then(function (response) {
                $scope.surveyVariationIndex = response.data.surveyVariationIndex;
                $scope.surveyCompleted = response.data.surveyCompleted;
                $scope.surveyShow = !$scope.surveyCompleted && ($scope.surveyVariationIndex < $scope.surveyVariations.length);
            }, function (error) {
                console.error('Error fetching survey status:', error);
            });
    };
    $scope.fetchSurveyStatus();

    $scope.closeSurvey = function () {
        if (!$scope.surveyCompleted) {
            $scope.surveyVariationIndex++;
            $http.post('/dashboard/survey_status', { surveyVariationIndex: $scope.surveyVariationIndex })
                .then(function (response) {
                    $scope.surveyShow = false;
                }, function (error) {
                    console.error('Error:', error);
                });
        }
    };

    $scope.surveyClicked = function () {
        $http.post('/dashboard/survey_clicked')
            .then(function (response) {
                $scope.surveyCompleted = true;
                $scope.surveyShow = false;
            }, function (error) {
                console.error('Error:', error);
            });
    };
}
