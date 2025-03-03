export function EndpointExceptionController ($scope, $http, menuService, paginationService, endpointService) {
    Prism.plugins.NormalizeWhitespace.setDefaults({
        'remove-trailing': false,
        'remove-indent': false,  
        'left-trim': true,
        'right-trim': true
    });
    
    endpointService.reset();
    menuService.reset('endpoint_exception');
    $scope.id2Function = {};

    $scope.table = [];

    endpointService.onNameChanged = function (name) {
        $scope.title = 'Exceptions for ' + name;
    };

    paginationService.init('exceptions');
    $http.get('api/num_exceptions/'+ endpointService.info.id).then(function (response) {
        paginationService.setTotal(response.data);
    });

    paginationService.onReload = function () {
        $http.get('api/detailed_exception_info/' + endpointService.info.id + '/' + paginationService.getLeft() + '/' + paginationService.perPage)
            .then(function (response) {
                $scope.table = response.data;
                $scope.id2Function = {};
            });
    };

    $scope.getUniqueKey = function (function_definition_id, full_stack_trace_id) {
        return `code_${function_definition_id}_${full_stack_trace_id}`;
    };

    $scope.getFunctionById = function (function_id, full_stack_trace_id) {
        let key = $scope.getUniqueKey(function_id, full_stack_trace_id);
        
        if ($scope.id2Function[key] === undefined){
            $http.get(`api/function_definition/${function_id}/${full_stack_trace_id}`)
                .then((response) => {
                    $scope.id2Function[key] = response.data;
                    $scope.$applyAsync(() => {
                        let element = document.getElementById(key);
                        Prism.highlightElement(element);
                    });
                });
        }
    };

    $scope.deleteExceptionById = function (full_stack_trace_id){
        if (full_stack_trace_id && confirm("Are you sure you want to delete exception?")){
            $http.delete(`api/exception_info/${full_stack_trace_id}`)
            .then((_) => {
                paginationService.onReload();
                paginationService.total--;
            });
        }
    };

    $scope.collapseAllDetails = function(name) {
       document.querySelectorAll(`#details_${name}`).forEach(details => {
           details.open = false;
       });
    };
};
