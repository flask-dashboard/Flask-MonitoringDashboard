function ApiPerformanceController($scope, $http, menuService, formService, infoService,
                                  plotlyService, endpointService) {
    endpointService.reset();
    menuService.reset('api_performance');
    $scope.title = 'API Performance';

    // Set the information box
    infoService.axesText = 'The X-axis presents the execution time in ms. The Y-axis presents every endpoint of ' +
        'the Flask application.';
    infoService.contentText = 'In this graph, it is easy to compare the execution time of the different endpoints ' +
        'across each other. This information can be used to validate which endpoints needs to be improved.';

    // Set the form handler
    formService.clear();
    formService.addEndpoints();

    formService.setReload(function () {
        $http.post('api/api_performance', {
            data: {
                endpoints: formService.getMultiSelection('endpoints')
            }
        }).then(function (response) {
            let data = response.data.map(obj => {
                return {
                    x: obj.values,
                    type: 'box',
                    name: obj.name,
                };
            });

            plotlyService.chart(data, {
                xaxis: {
                    title: 'Execution time (ms)',
                },
                yaxis: {
                    type: 'category'
                }
            });
        });
    });
}