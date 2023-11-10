export function SurveyController($scope, $http) {
    $scope.UUID = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'

    var config = {
        headers: {
            'X-Parse-Application-Id': '',
            'X-Parse-REST-API-Key': '',
            'Content-Type': 'application/json'
        }
    };

    $scope.surveyShow = false;

    $scope.fetchSurveyStatus = function () {
        var queryParams = {
            UUID: $scope.UUID
        };

        var queryString = encodeURIComponent(JSON.stringify(queryParams));

        return $http.get(`https://parseapi.back4app.com/classes/Test1?where=${queryString}`, config)
            .then(function (response) {
                if (response.data.results && response.data.results.length > 0) {
                    if (response.data.results[0].showSurvey === true) {
                        console.log(response.data)
                        $scope.surveyShow = true;
                    }
                } else {
                    console.error('No survey records found.');
                }
            }, function (error) {
                console.error('Error fetching consent:', error);
            });
    };

    $scope.fetchSurveyStatus();

    // Doesn't work yet
    $scope.closeSurvey = function () {
        $scope.fetchSurveyStatus()
            .then(function (response) {
                var survey = response.data.results.find(function (item) {
                    return item.UUID === $scope.UUID;
                });

                if (survey && survey.objectId) {
                    return $http.put(`https://parseapi.back4app.com/classes/Test1/${survey.objectId}`,
                        { showSurvey: false }, config);
                } else {
                    throw new Error('No matching survey found.');
                }
            })
            .then(function (response) {
                console.log('Survey closed recorded:', response.data);
                $scope.surveyShow = false;
            })
            .catch(function (error) {
                console.error('Error:', error);
            });
    };
}
