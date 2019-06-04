function HostPerformanceController($scope, $http, menuService, formService, infoService,
                                  plotlyService, endpointService) {
    endpointService.reset();
    menuService.reset('host_performance');
    $scope.title = 'Host Performance';

    // Set the information box
    infoService.axesText = 'The X-axis presents the execution time in ms. The Y-axis presents every connected host of' +
        ' the Flask application.';
    infoService.contentText = 'In this graph, it is easy to compare the execution times of different endpoints. ' +
        'This information can be used to discover which endpoints need to be improved in terms ' +
        'of response times.';

    // Set the form handler
    formService.clear();
    formService.addEndpoints();

    formService.setReload(function () {
        $http.post('api/host_performance', {
            data: {
                ids: [1, 2, 3, 4, 5, 6, 7, 8, 9]
            }
        }).then(function (response) {
            console.log(response.data);
            let data = response.data.map(obj => {
                return {
                    x: obj.values,
                    type: 'box',
                    name: obj.name,
                    id: obj.id
                };
            });

            console.log(data);

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