export function CustomGraphController($scope, $http, infoService, endpointService,
                               menuService, formService, plotlyService) {
    endpointService.reset();
    menuService.reset('custom_graph' + endpointService.graphId);
    $scope.title = endpointService.getGraphTitle();
    endpointService.onNameChanged = function (name) {
        $scope.title = name;
    };

    // Set the information box
    infoService.axesText = '';
    infoService.contentText = '';

    formService.clear();
    let startDate = formService.addDate('Start date');
    startDate.value.setDate(startDate.value.getDate() - 14);
    formService.addDate('End date');

    formService.setReload(function () {
        let start = formService.getDate('Start date');
        let end = formService.getDate('End date');

        $http.get('api/custom_graph/' + endpointService.graphId + '/' + start + '/' + end)
            .then(function (response) {
                let values = response.data.map(o => o.value);
                let times = response.data.map(o => o.time);
                plotlyService.chart([{
                    x: times,
                    y: values,
                    type: 'bar',
                    name: $scope.title
                }], {
                    yaxis: {
                        title: 'Values',
                    },
                    margin: {
                        l: 100
                    }
                });
            });
    });
    formService.reload();
}