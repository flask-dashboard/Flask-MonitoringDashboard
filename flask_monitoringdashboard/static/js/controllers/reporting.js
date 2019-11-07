function offsettedDate(date, offsetInDays) {
    const copy = new Date(date);
    copy.setDate(date.getDate() + offsetInDays);

    return copy;
}


function ReportingController($scope, $http, $location, DTOptionsBuilder, menuService, endpointService, plotlyService) {
    endpointService.reset();
    menuService.reset('reporting');

    const now = new Date();

    $scope.reports = {};

    $scope.activeSection = 'week';

    $scope.monthName = moment().format('MMMM');
    $scope.previousMonthName = moment().subtract(1, 'months').format('MMMM');

    $scope.currentDay = moment().format('MMM DD');
    $scope.yesterday = moment().subtract(1, 'days').format('MMM DD');

    $scope.currentWeekNumber = moment().isoWeek();
    $scope.previousWeekNumber = moment().subtract(1, 'weeks').isoWeek();

    $scope.generating = false;
    $scope.onlyShowInteresting = true;


    $scope.activeSection = 'custom';
    $scope.intervals = intervals(1, 'months');


    function intervals(q, units) {
        const t1 = moment()
            .subtract(q, units)
            .startOf(units);

        const t2 = moment().subtract(q, units).endOf(units);
        const t3 = moment().startOf(units);
        const t4 = moment().endOf(units);

        return {
            "comparison_interval": {
                "from": t3.toDate(),
                "to": t4.toDate()
            },
            "compared_to_interval": {
                "from": t1.toDate(),
                "to": t2.toDate()
            }
        }
    }

    $scope.selectSection = function (section) {
        $scope.activeSection = section;

        const INTERVAL_SIZES = {
            day: [1, 'days'],
            week: [1, 'isoWeeks'],
            month: [1, 'months'],
            custom: [1, 'isoWeeks'],
        };

        const intervalSize = INTERVAL_SIZES[$scope.activeSection];

        $scope.intervals = intervals(intervalSize[0], intervalSize[1])
    };

    $scope.selectEntry = function (summary, answer) {
        $scope.selectedSummary = summary;
        $scope.selectedAnswer = answer;

        const {comparison_interval, compared_to_interval} = answer.latencies_sample;

        const data = [
            {name: 'Comparison Interval', type: 'violin', y: comparison_interval},
            {name: 'Compared To Interval', type: 'violin', y: compared_to_interval}
        ];

        plotlyService.chart(data, {
            xaxis: {
                title: 'Execution time (ms)',
            },
        });
    };

    $scope.generateReport = function () {
        $scope.generating = true;

        $http.post(`/dashboard/api/reporting/make_report`, {
            compared_to_interval: {
                to: parseInt(`${$scope.intervals.compared_to_interval.to.getTime() / 1000}`),
                from: parseInt(`${$scope.intervals.compared_to_interval.from.getTime() / 1000}`),
            },
            comparison_interval: {
                to: parseInt(`${$scope.intervals.comparison_interval.to.getTime() / 1000}`),
                from: parseInt(`${$scope.intervals.comparison_interval.from.getTime() / 1000}`),
            }
        })
            .then(response => {
                $scope.reports[$scope.activeSection] = response.data;

                $scope.generating = false;
            });
    };
}