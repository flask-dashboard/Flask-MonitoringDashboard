function StatusCodeDistributionController($scope, $http, infoService, endpointService, menuService, formService, plotlyService, $filter) {
    menuService.reset('status_code_distribution');
    endpointService.reset();

    formService.setReload(function () {
        var endpointId = endpointService.info.id;

        $http.get('api/endpoint_status_code_summary/' + endpointId).then(function (response) {

            var layout = {
                height: 400,
                width: 500,
            };

            var distribution = response.data.distribution;

            var statusCodes = Object.keys(distribution);

            var data = [{
                values: statusCodes.map(statusCode => distribution[statusCode]),
                labels: statusCodes,
                type: 'pie'
            }];

            $scope.hello = 'hello, world';
            $scope.error_requests = response.data.error_requests;


            plotlyService.chart(data, layout);
        });
    });

    formService.reload();
}