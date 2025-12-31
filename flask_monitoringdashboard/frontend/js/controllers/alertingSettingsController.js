export function AlertingSettingsController($scope, $http, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('alerting_settings');

    $scope.alert_config = {};

    $scope.labels = {
        'alert_type': 'Alert type',
        'smtp_host': 'SMTP host',
        'smtp_port': 'SMTP port',
        'smtp_user': 'SMTP user',
        'smtp_to': 'SMTP \'to\' address(es)',
        'repository_owner': 'GitHub repository owner',
        'repository_name': 'GitHub repository name',
        'chat_platform': 'Chat platform'
    };

    $http.get('api/deploy_alert_config').then(function (response) {
        $scope.alert_config = response.data;
        $scope.alert_type = $scope.alert_config['alert_type'];
        $scope.labels['alert_type'] += $scope.alert_type.length > 1 ? 's' : '';
        $scope.alert_config = joinAllListsToStrings($scope.alert_config);
    });

    // Helper function to recursively join all list values
    // in the config to strings.
    function joinAllListsToStrings(obj) {
        if (obj instanceof Array) {
            return obj.join(', ');
        }
        if (typeof obj === 'object' && obj !== null) {
            const result = {};
            Object.keys(obj).forEach(function (key) {
                result[key] = joinAllListsToStrings(obj[key]);
            });
            return result;
        }
        return obj;
    }

}
