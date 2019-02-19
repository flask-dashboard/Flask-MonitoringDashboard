'use strict';

app.controller('MenuController', function ($scope, menuService) {
    $scope.menu = menuService;
});

app.controller('InfoController', function ($scope, infoService) {
    $scope.info = infoService;
});

app.controller('FormController', function ($scope, formService) {
    $scope.handler = formService;
});

app.controller('EndpointController', function ($scope, endpointService) {
    $scope.endpoint = endpointService;
});

app.controller('PaginationController', function ($scope, paginationService) {
    $scope.pagination = paginationService;
});