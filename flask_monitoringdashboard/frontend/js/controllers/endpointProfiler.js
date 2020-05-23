export function EndpointProfilerController($scope, $http, menuService, endpointService,
                                    paginationService, formService) {
    endpointService.reset();

    // TODO: refactor endpointProfiler and endpointGroupedProfiler

    endpointService.onNameChanged = function (name) {
        $scope.title = 'Profiler for ' + name;
    };
    menuService.reset('endpoint_profiler');

    paginationService.init('requests');
    $http.get('api/num_profiled/' + endpointService.info.id).then(function (response) {
        paginationService.setTotal(response.data);
    });
    paginationService.onReload = function () {
        formService.isLoading = true;
        $http.get('api/profiler_table/' + endpointService.info.id + '/' +
            paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
            formService.isLoading = false;
            // Add more properties
            for (let req of $scope.table) {
                let rows = req.stack_lines;
                for (let row of rows) {
                    row.min = parseInt(row.indent) === 0;     // show min- or plus-button
                    row.showRow = parseInt(row.indent) < 2; // completely show or hide the row
                    row.body = getBody(rows, parseInt(row.position)); // lines that must be minimized
                }
            }
        });
    };

    $scope.buttonText = function (request) {
        return request.stack_lines.every(i => i.showRow) ? 'Hide all' : 'Expand all';
    };

    $scope.toggleButton = function (request) {
        if (request.stack_lines.every(i => i.showRow)) { // hide
            for (let row of request.stack_lines) {
                row.min = parseInt(row.indent) === 0;
                row.showRow = parseInt(row.indent) < 2;
            }
        } else { // show
            for (let row of request.stack_lines) {
                row.showRow = true;
                row.min = true;
            }
        }
    };

    $scope.toggleRows = function (request, row) {
        if (row.min) { // minimize
            for (let i of row.body) {
                request.stack_lines[i].min = false;
                request.stack_lines[i].showRow = false;
            }
        } else { // maximize
            for (let i of row.body) {
                request.stack_lines[i].showRow =
                    parseInt(request.stack_lines[i].indent) === parseInt(row.indent) + 1;
            }
        }

        row.min = !row.min;
    };

    let getBody = function (rows, j) {
        let body = [];
        let index = j + 1;
        while (index < rows.length && parseInt(rows[index].indent) > parseInt(rows[j].indent)) {
            body.push(index);
            index += 1;
        }
        return body;
    };

    $scope.computeColor = function (percentage) {
        let red = [230, 74, 54];
        let green = [198, 220, 0];

        let r = red[0] * percentage + green[0] * (1 - percentage);
        let g = red[1] * percentage + green[1] * (1 - percentage);
        let b = red[2] * percentage + green[2] * (1 - percentage);
        return 'rgb(' + r + ', ' + g + ', ' + b + ')';
    };
}