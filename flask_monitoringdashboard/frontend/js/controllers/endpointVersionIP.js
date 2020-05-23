export function EndpointVersionIPController($scope, $http, infoService, endpointService,
                                     menuService, formService, plotlyService, $filter) {
    endpointService.reset();
    menuService.reset('endpoint_ip');
    endpointService.onNameChanged = function (name) {
        $scope.title = 'IP-Focused Multi-Version Performance for ' + name;
    };

    // Set the information box
    infoService.axesText = 'In this graph, the X-axis presents the versions that are used. The Y-axis presents ' +
        '(a subset of) all IP-addresses. You can use the slider to select a subset of the all IP-addresses.';
    infoService.contentText = 'The cell color represents the average response time (expressed in ms) of this endpoint ' +
        'per IP per version.';

    formService.clear();
    formService.addIP();
    formService.addVersions(endpointService.info.id);

    formService.setReload(function () {
        $http.post('api/version_ip/' + endpointService.info.id, {
            data: {
                versions: formService.getMultiSelection('versions'),
                ip: formService.getMultiSelection('IP-addresses')
            }
        }).then(function (response) {
            let versions = response.data.versions.map(
                obj => obj.version + '<br>' + $filter('dateLayout')(obj.date)
            );
            plotlyService.heatmap(versions,
                formService.getMultiSelection('IP-addresses'), response.data.data, {
                    xaxis: {
                        type: 'category',
                        title: 'Versions'
                    },
                    yaxis: {
                        type: 'category',
                        title: 'IP-addresses'
                    }
                });
        });
    });
}