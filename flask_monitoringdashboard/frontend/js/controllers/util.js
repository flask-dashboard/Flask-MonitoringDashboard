export function MenuController($scope, menuService) {
    $scope.menu = menuService;
}

export function InfoController($scope, infoService) {
    $scope.info = infoService;
}

export function FormController($scope, formService) {
    $scope.handler = formService;
}

export function EndpointController($scope, endpointService) {
    $scope.endpoint = endpointService;
}

export function PaginationController($scope, paginationService) {
    $scope.pagination = paginationService;
}