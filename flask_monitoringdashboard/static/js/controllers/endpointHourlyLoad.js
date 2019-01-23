function EndpointHourlyLoadController($scope, $http, menuService, endpointService,
                                      infoService, formService, plotlyService) {
    endpointService.reset();
    menuService.reset('endpoint_hourly');
    endpointService.onNameChanged = function (name) {
        $scope.title = 'Hourly API Utilization for ' + name;
    };

    // Set the information box
    infoService.axesText = 'The X-axis presents a number of days. The Y-axis presents every hour of the day.';
    infoService.contentText = 'The color of the cell presents the number of requests that the application ' +
        'received in a single hour. The darker the cell, the more requests it has processed. This information ' +
        'can be used to validate on which moment of the day the Flask application processes to most requests.';

    // Set the form handler
    formService.clear();
    let start = formService.addDate('Start date');
    formService.addDate('End date');
    start.value.setDate(start.value.getDate() - 14);

    formService.setReload(function () {
        let start = formService.getDate('Start date');
        let end = formService.getDate('End date');
        let times = [...Array(24).keys()].map(d => d + ":00 ");

        $http.get('api/hourly_load/' + start + '/' + end + '/' + endpointService.info.id)
            .then(function (response) {
                plotlyService.heatmap(response.data.days, times, response.data.data, {

                    xaxis: {
                        type: 'category',
                        title: 'Versions'
                    },
                    yaxis: {
                        type: 'category',
                        autorange: 'reversed'
                    }

                });
            });
    });
    formService.reload();
}