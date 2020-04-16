export function HourlyLoadController($scope, $http, menuService, plotlyService, infoService,
                              formService, endpointService, $filter) {
    endpointService.reset();
    menuService.reset('hourly_load');
    $scope.title = 'Hourly API Utilization';

    // Set the information box
    infoService.axesText = 'The X-axis represents the dates. The Y-axis presents the hours of the day.';
    infoService.contentText = 'The cell color represents the number of requests that the application ' +
        'received in a single hour. The darker the cell, the more requests it has processed. This information ' +
        'can be used to to discover the peak usage hours of the Flask application.';

    // Set the form handler
    formService.clear();
    let start = formService.addDate('Start date');
    formService.addDate('End date');
    start.value.setDate(start.value.getDate() - 14);

    formService.setReload(function () {
        let start = formService.getDate('Start date');
        let end = formService.getDate('End date');
        let times = [...Array(24).keys()].map(d => d + ":00");
        $http.get('api/hourly_load/' + start + '/' + end).then(function (response) {
            let x = response.data.days;
            let y = times;
            let z = response.data.data;
            let hover_text = z.map((row, i) => row.map((item, j) => {
              return `Date: ${$filter('dateShort')(x[j])}<br>Time: ${i + ':00'}<br>Requests: ${item}`
            }));

            plotlyService.heatmap(x, y, z, {
                yaxis: {
                    autorange: 'reversed'
                },
                margin: {l: 50}
            }, hover_text);
        });
    });
    formService.reload();
}
