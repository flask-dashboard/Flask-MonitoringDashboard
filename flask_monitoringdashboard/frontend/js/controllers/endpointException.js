export function EndpointExceptionController ($scope, $http, menuService, paginationService, endpointService, plotlyService) {
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
        $http.get('api/detailed_exception_info/' + endpointService.info.id + '/' + paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
        });
    };

    $scope.getUniqueKey = function (function_definition_id, full_stack_trace_id) {
        return `code_${function_definition_id}_${full_stack_trace_id}`;
    }

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
    }
    
    //Mock data for chart-test
    let mockResponse = {
        data: [
            { value: 10, time: 'date 1'},
            { value: 15, time: 'date 2'},
            { value: 20, time: 'date 3'},
            { value: 10, time: 'date 4'},
            { value: 15, time: 'date 5'},
            { value: 20, time: 'date 6'},
            { value: 10, time: 'date 7'},
            { value: 5, time: 'date 8'},
            { value: 2, time: 'date 9'},
            { value: 10, time: 'date 10'},
            { value: 15, time: 'date 11'},
            { value: 20, time: 'date 12'}
        ]
    };
    //Chart with mock data:
    $http.get('api/exception_graph/' + endpointService.info.id).then(function (response) {
        let values = mockResponse.data.map(o => o.value);
        let times = mockResponse.data.map(o => o.time);
        plotlyService.chart([{
                x: times,
                y: values,
                type: 'bar',
        }], {
            xaxis: {
                title: 'date',
                showticklabels: false
            },
            yaxis: {
                title: 'occurences',
            },
            margin: {
                l: 700,
                r: 500
            },
            height: 300,
        });
    });
    
};
