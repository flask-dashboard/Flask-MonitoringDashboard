export function EndpointUsersController($scope, $http, infoService, endpointService,
                                 menuService, formService, plotlyService) {
    endpointService.reset();
    menuService.reset('endpoint_user');
    endpointService.onNameChanged = function (name) {
        $scope.title = 'Per-User Performance for ' + name;
    };

    // Set the information box
    infoService.axesText = 'The X-axis presents the execution time in ms. The Y-axis presents the versions that are used.';
    infoService.contentText = 'This graph shows a horizontal boxplot for the versions that are used. With this ' +
        'graph you can found out whether the performance changes across different versions.';

    formService.clear();
    formService.addUsers();

    formService.setReload(function () {
        $http.post('api/endpoint_users/' + endpointService.info.id, {
            data: {
                users: formService.getMultiSelection('users'),
            }
        }).then(function (response) {
            plotlyService.chart(response.data.map(row => {
                return {
                    x: row.values,
                    type: 'box',
                    name: row.user,
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