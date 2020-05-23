export function MonitorLevelController($scope, $http) {

    $scope.sendForm = function (value) {
        $scope.value = value;
        $http.post('api/set_rule',
            $.param({
                'name': $scope.name,
                'value': value
            }),
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                }
            });
    };

    $scope.computeColor = function (level) {
        let a = 0.2;
        if ($scope.value === level) {
            a = 1;
        }

        let red = [230, 74, 54];
        let green = [237, 255, 77];

        // level 0 = total green, level 3 = total red
        let percentage = level / 3.0;
        let r = red[0] * percentage + green[0] * (1 - percentage);
        let g = red[1] * percentage + green[1] * (1 - percentage);
        let b = red[2] * percentage + green[2] * (1 - percentage);

        return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + a + ')';
    };
}

