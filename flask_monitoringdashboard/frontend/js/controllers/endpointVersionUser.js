export function EndpointVersionUserController($scope, $http, infoService, endpointService,
                                       menuService, formService, plotlyService, $filter) {
    endpointService.reset();
    menuService.reset('endpoint_user_version');
    endpointService.onNameChanged = function (name) {
        $scope.title = 'User-Focused Multi-Version Performance for ' + name;
    };

    // Set the information box
    infoService.axesText = 'In this graph, the X-axis presents the versions that are used. The Y-axis ' +
        'presents (a subset of) all unique users, as specified by "dashboard.config.group_by". You can ' +
        'use the slider to select a subset of the all unique users.';
    infoService.contentText = 'The cell color represents the average response time (expressed in ms) of this endpoint ' +
        'per user per version.';

    formService.clear();
    formService.addUsers();
    formService.addVersions(endpointService.info.id);

    formService.setReload(function () {
        $http.post('api/version_user/' + endpointService.info.id, {
            data: {
                versions: formService.getMultiSelection('versions'),
                users: formService.getMultiSelection('users')
            }
        }).then(function (response) {
            let versions = response.data.versions.map(
                obj => obj.version + '<br>' + $filter('dateLayout')(obj.date)
            );
            plotlyService.heatmap(versions,
                formService.getMultiSelection('users'),
                response.data.data, {
                    xaxis: {
                        type: 'category',
                        title: 'Versions'
                    },
                    yaxis: {
                        type: 'category',
                        title: 'Users',
                        autorange: 'reversed'
                    }
                });
        });
    });
}