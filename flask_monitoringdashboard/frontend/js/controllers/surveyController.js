export function SurveyController($scope, $http, $sce) {
    $scope.surveyShow = false;
    $scope.surveyCompleted = false;

    // Fetch local storage variation index
    const storedIndex = localStorage.getItem('surveyVariationIndex');
    $scope.surveyVariationIndex = storedIndex && !isNaN(parseInt(storedIndex)) ? parseInt(storedIndex) : 0;

    // Variations of the survey prompt
    $scope.surveyVariations = [
        'Please take a moment to <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">fill out our survey</a>.',
        'Your feedback is valuable! <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">Take our quick survey.</a>',
        'We value your opinion! Click <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">here</a> to share your thoughts.',
        'Help us improve! Participate in our <a href="https://forms.gle/kWD5mqcibS2V5f3Y6" target="_blank">short survey</a>.'
    ];

    // Mark as trusted HTML
    $scope.surveyVariations = $scope.surveyVariations.map(variation =>
        $sce.trustAsHtml(variation)
    );

    // Fetches to check if the survey is filled from database
    $scope.fetchSurveyFilled = function () {
        $http.get('/dashboard/telemetry/get_is_survey_filled')
            .then(function (response) {
                $scope.surveyCompleted = response.data.is_survey_filled;
                $scope.surveyShow = !$scope.surveyCompleted && ($scope.surveyVariationIndex < $scope.surveyVariations.length);
            }, function (error) {
                console.error('Error fetching survey status:', error);
            });
    };
    $scope.fetchSurveyFilled();

    // Increment surveyVariation in localStorage
    $scope.closeSurvey = function () {
        if (!$scope.surveyCompleted) {
            $scope.surveyVariationIndex++;
            localStorage.setItem('surveyVariationIndex', $scope.surveyVariationIndex.toString());
        }
    };

    // Mark survey as filled in database
    $scope.surveyFilled = function () {
        $http.get('/dashboard/telemetry/survey_has_been_filled')
            .then(function (response) {
            }, function (error) {
                console.error('Error:', error);
            });
        $scope.surveyCompleted = true;
        $scope.surveyShow = false;
    };
}