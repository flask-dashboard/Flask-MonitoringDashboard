export function EndpointVersionController($scope, $http, infoService, endpointService,
                                   menuService, formService, plotlyService, $filter) {
    endpointService.reset();
    menuService.reset('endpoint_version');
    endpointService.onNameChanged = function (name) {
        $scope.title = 'Per-Version Performance for ' + name;
    };

    // Set the information box
    infoService.axesText = 'The X-axis presents the execution time in ms. The Y-axis presents the versions that are used.';
    infoService.contentText = 'This graph shows a horizontal boxplot for the versions that are used. With this ' +
        'graph you can found out whether the performance changes across different versions.';

    formService.clear();
    formService.addVersions(endpointService.info.id);

    formService.setReload(function () {
        $http.post('api/endpoint_versions/' + endpointService.info.id, {
            data: {
                versions: formService.getMultiSelection('versions'),
            }
        }).then(function (response) {
            plotlyService.chart(response.data.map(row => {
                return {
                    x: row.values,
                    type: 'box',
                    name: row.version + '<br>' + ($filter('dateLayout')(row.date)),
                    marker: {color: row.color}
                };
            }), {
                xaxis: {
                    title: 'Execution time (ms)',
                },
                yaxis: {
                    type: 'category',
                    autorange: 'reversed'
                },
                margin: {
                    l: 200
                }
            });
        });
    });
}