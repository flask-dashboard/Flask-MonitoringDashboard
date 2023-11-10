export function SurveyController($scope, $http) {
    $scope.surveyShow = false;

    $scope.fetchSurveyStatus = function () {
        return $http.post('/dashboard/get_survey_filled')
            .then(function (response) {
                $scope.surveyShow = !response.data.get_survey_filled;
            }, function (error) {
                console.error('Error fetching survey status:', error);
            });
    };
    $scope.fetchSurveyStatus();

    $scope.closeSurvey = function () {
        $http.post('/dashboard/survey_filled')
            .then(function (response) {
                $scope.surveyShow = false;
            }, function (error) {
                $scope.surveyShow = false;
                console.error('Error:', error);
            });
    };

}
