export function MultiVersionController($scope, $http, menuService, formService, infoService,
                                plotlyService, endpointService) {
    endpointService.reset();
    menuService.reset('multi_version');
    $scope.title = 'Multi version API Utilization';

    // Set the information box
    infoService.axesText = 'The X-axis presents the versions that are used. The Y-axis presents the' +
        'endpoints that are found in the Flask application.';
    infoService.contentText = 'The color of the cell presents the distribution of the amount of requests ' +
        'that the application received in a single version for a single endpoint. The darker the cell, ' +
        'the more requests a certain endpoint has processed in that version. Since it displays the ' +
        'distribution of the load, each column sums up to 100%. This information can be used to discover ' +
        'which endpoints process the most requests.';

    // Set the form handler
    formService.clear();
    formService.addVersions();
    formService.addEndpoints();

    formService.setReload(function () {
        let versions = formService.getMultiSelection('versions');
        let endpoints = formService.getMultiSelection('endpoints');
        $http.post('api/multi_version', {
            data: {
                versions: versions,
                endpoints: endpoints
            }
        }).then(function (response) {
            plotlyService.heatmap(versions, endpoints,
                response.data.map(l => l.map(i => i == 0 ? 'NaN' : i)), {
                    xaxis: {
                        type: 'category',
                        title: 'Versions'
                    },
                    yaxis: {
                        type: 'category'
                    }
                });
        });
    });
}