export function DailyUtilizationController($scope, $http, menuService, formService, infoService,
                                    plotlyService, endpointService) {
    endpointService.reset();
    menuService.reset('daily_load');
    $scope.title = 'Daily API Utilization';

    // Set the information box
    infoService.axesText = 'The X-axis presents the amount of requests. The Y-axis presents a number of days.';
    infoService.contentText = 'This graph presents a horizontal stacked barplot. Each endpoint is represented ' +
        'by a color. In the legend on the right, you can disable a certain endpoint by clicking on it. You can ' +
        'also show in the information of a single endpoint by double clicking that endpoint in the legend. The ' +
        'information from this graph can be used to see on which days (a subset of) the endpoints are used the most.';

    // Set the form handler
    formService.clear();
    let start = formService.addDate('Start date');
    start.value.setDate(start.value.getDate() - 10);
    formService.addDate('End date');

    formService.setReload(function () {
        let start = formService.getDate('Start date');
        let end = formService.getDate('End date');

        $http.get('api/requests/' + start + '/' + end).then(function (response) {
            let data = response.data.data.map(obj => {
                return {
                    x: obj.values,
                    y: response.data.days,
                    name: obj.name,
                    type: 'bar',
                    orientation: 'h'
                };
            });

            plotlyService.chart(data, {
                barmode: 'stack',
                xaxis: {
                    title: 'Number of requests',
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