function StatusCodeDistributionController($scope, $http, infoService, endpointService, menuService, formService, plotlyService, $filter) {
    menuService.reset('status_code_distribution');

    var matches = /endpoint\/(\d+)\/status_code_distribution/g.exec(window.location.toString());

    var endpointId = parseInt(matches[1]);


    $http.get('api/endpoint_status_code_distribution/' + endpointId).then(function (response) {
        var layout = {
            height: 400,
            width: 500
        };

        const statusCodes = Object.keys(response.data);

        var data = [{
            values: statusCodes.map(statusCode => response.data[statusCode]),
            labels: statusCodes,
            type: 'pie'
        }];


        plotlyService.chart(data, layout);
    });
}