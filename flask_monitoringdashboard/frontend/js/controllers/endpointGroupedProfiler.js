export function EndpointGroupedProfilerController($scope, $http, menuService,
                                           endpointService, formService) {
    endpointService.reset();
    $scope.table = [];

    endpointService.onNameChanged = function (name) {
        $scope.title = 'Grouped profiler for ' + name;
    };
    menuService.reset('endpoint_grouped_profiler');

    $http.get('api/grouped_profiler/' + endpointService.info.id).then(function (response) {
        formService.isLoading = false;
        $scope.table = response.data;
        for (let i = 0; i < $scope.table.length; i++) {
            let row = $scope.table[i];
            row.min = parseInt(row.indent) === 0;     // show min- or plus-button
            row.showRow = parseInt(row.indent) < 2; // completely show or hide the row
            row.body = getBody($scope.table, i); // lines that must be minimized
        }

        let sunburst = makeSunburst($scope.table, 0);
        const color = d3.scaleOrdinal(d3.schemeCategory20);

        Sunburst()
            .data(sunburst)
            .label('name')
            .size('size')
            .color((d, parent) => color(parent ? parent.data.name : null))
            .tooltipContent((d, node) => {
                return 'Size: <i>' + node.value + '</i>';
            })
            (document.getElementById('sunburst'));
    });

    let makeSunburst = function (data, indent) {
        if (indent === 0) {
            let i = 0;
            while (i + 1 < data.length && parseInt(data[i + 1].indent) === 0) {
                i++;
            }
            return {
                name: data[i].code,
                children: makeSunburst(data[i].body.map(i => $scope.table[i]), 1)
            };
        } else {
            let children = [];
            for (let row of data) {
                if (parseInt(row.indent) === indent) {
                    if (row.body.length > 0) {
                        children.push({
                            name: row.code,
                            children: makeSunburst(row.body.map(i => $scope.table[i]), indent + 1)
                        });
                    } else {
                        children.push({
                            name: row.code,
                            size: Math.max(row.duration, 1)
                        })
                    }
                }
            }
            return children
        }
    };
    $scope.buttonText = function () {
        return $scope.table.every(i => i.showRow) ? 'Hide all' : 'Expand all';
    };

    $scope.toggleButton = function () {
        if ($scope.table.every(i => i.showRow)) { // hide
            for (let row of $scope.table) {
                row.min = parseInt(row.indent) === 0;
                row.showRow = parseInt(row.indent) < 2;
            }
        } else { // show
            for (let row of $scope.table) {
                row.showRow = true;
                row.min = true;
            }
        }
    };

    $scope.toggleRows = function (row) {
        if (row.min) { // minimize
            for (let i of row.body) {
                $scope.table[i].min = false;
                $scope.table[i].showRow = false;
            }
        } else { // maximize
            for (let i of row.body) {
                $scope.table[i].showRow =
                    parseInt($scope.table[i].indent) === parseInt(row.indent) + 1;
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