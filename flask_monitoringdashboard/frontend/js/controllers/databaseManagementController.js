const HEADERS = {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
    }
};

export function DatabaseManagementController($scope, $http, menuService, endpointService, modalService) {
    endpointService.reset();
    menuService.reset('database_management');

    $scope.renderChart = function (data, totalSize) {
        const ctx = document.getElementById('databaseUsageChart').getContext('2d');
        const labels = data.map(item => item.endpoint);
        const sizes = data.map(item => item.size);

        // Generate a color for each endpoint
        const backgroundColors = data.map((_, index) => generateColor(index));
        const borderColors = backgroundColors.map(color => color.replace(/0.2\)$/, '1)'));

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Endpoint size',
                    data: sizes,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    datalabels: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += `${context.parsed} bytes`;
                                }
                                return label;
                            }
                        }
                    }
                },
                cutout: '50%',
                animation: {
                    onComplete: function () {
                        const ctx = this.ctx;
                        ctx.font = '16px Arial';
                        ctx.fillStyle = 'black';
                        ctx.textAlign = 'center';
                        ctx.fillText(`Total Size: ${totalSize} bytes`, this.chartArea.left + (this.chartArea.right - this.chartArea.left) / 2, this.chartArea.top + (this.chartArea.bottom - this.chartArea.top) / 2);
                        ctx.fillText(`Endpoints: ${data.length}`, this.chartArea.left + (this.chartArea.right - this.chartArea.left) / 2, this.chartArea.top + (this.chartArea.bottom - this.chartArea.top) / 2 + 20);
                    }
                }
            }
        });
    };

    function generateColor(index) {
        const hue = index * 137.508; // Golden angle approximation for distribution
        return `hsla(${hue}, 50%, 60%, 0.2)`;
    }

    $scope.fetchChartData = function () {
        $http.get('/database_management/get_database_tables_size', HEADERS)
            .then(function (response) {
                const responseData = response.data;
                const totalSize = responseData.total_size;
                delete responseData.total_size; 

                // Convert response data to the expected format for renderChart
                const chartData = Object.keys(responseData).map(table => ({
                    endpoint: table,
                    size: responseData[table]
                }));

                // Render chart with the new data format
                $scope.renderChart(chartData, totalSize);
            }, function (errorResponse) {
                console.error('Error fetching chart data:', errorResponse);
            });
    };
    $scope.fetchChartData();

    $scope.pruningConfig = {
        dayOfMonth: null,
        monthsBetweenRuns: null,
        ageThresholdWeeks: null,
        deleteFromCustomGraphs: false,
        hour: null
    };

    $scope.pruningMessage = '';
    $scope.pruningIsSuccess = false;


    // Validation for Day of the Month
    $scope.isValidDayOfMonth = function () {
        const dayOfMonth = $scope.pruningConfig.dayOfMonth;
        return dayOfMonth && dayOfMonth >= 1 && dayOfMonth <= 30;
    };

    // Validation for Months Between Runs
    $scope.isValidMonthsBetweenRuns = function () {
        const months = Number($scope.pruningConfig.monthsBetweenRuns);
        return !isNaN(months) && [1, 2, 3, 4, 6, 12].includes(months);
    };

    // Validation for Age Threshold in Weeks
    $scope.isValidAgeThresholdWeeks = function () {
        const age = $scope.pruningConfig.ageThresholdWeeks;
        return age && age > 0;
    };

    // Validation for Hour
    $scope.isValidHour = function () {
        const hour = $scope.pruningConfig.hour;
        return hour !== null && hour >= 0 && hour < 24;
    };


    $scope.updateAutomatedPruning = function () {
        $scope.submitAutomatedPruningAttempted = true;

        if (!$scope.isValidDayOfMonth() || !$scope.isValidMonthsBetweenRuns() || !$scope.isValidAgeThresholdWeeks() || !$scope.isValidHour()) {
            console.error('Invalid input');
            return;
        }

        // If all validations pass, proceed with the setup
        $http.post('/database_management/submit_prune_schedule',
            $.param($scope.pruningConfig),
            HEADERS
        ).then(function (successResponse) {
            $scope.pruningMessage = 'Prune schedule setup successful';
            $scope.pruningIsSuccess = true;
        }, function (errorResponse) {
            $scope.pruningMessage = 'Error setting up prune schedule:', errorResponse;
            $scope.pruningIsSuccess = false;
            console.error('Error in pruning on demand:', errorResponse);
        });
    };


    $scope.pruneOnDemandConfig = {
        ageThresholdWeeks: null,
        deleteCustomGraphs: false
    };

    // Validation for Age Threshold in Weeks
    $scope.isValidPruneOnDemandAgeThresholdWeeks = function () {
        const age = $scope.pruneOnDemandConfig.ageThresholdWeeks;
        return age && age > 0;
    };

    $scope.pruneOnDemandMessage = '';
    $scope.pruneOnDemandIsSuccess = false;

    $scope.pruneOnDemand = function () {
        $scope.submitPruningOnDemandAttempted = true;

        if (!$scope.isValidPruneOnDemandAgeThresholdWeeks()) {
            console.error('Invalid age threshold');
            return;
        }

        $http.post('/database_management/prune_on_demand',
            $.param($scope.pruneOnDemandConfig),
            HEADERS
        ).then(function (successResponse) {
            $scope.pruneOnDemandIsSuccess = true;
            $scope.pruneOnDemandMessage = 'Pruning successful';
        }, function (errorResponse) {
            $scope.pruneOnDemandMessage = 'Error in pruning on demand:', errorResponse;
            $scope.pruneOnDemandIsSuccess = true;
            console.error('Error in pruning on demand:', errorResponse);
        });
    };


}


