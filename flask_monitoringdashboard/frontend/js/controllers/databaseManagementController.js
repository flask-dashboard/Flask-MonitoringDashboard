const HEADERS = {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
    }
};

export function DatabaseManagementController($scope, $http, menuService, endpointService, modalService) {
    endpointService.reset();
    menuService.reset('database_management');

    $scope.renderChart = function (data) {
        const ctx = document.getElementById('databaseUsageChart').getContext('2d');
        const labels = data.map(item => item.endpoint);
        const sizes = data.map(item => item.size);
        const totalSize = sizes.reduce((a, b) => a + b, 0);
    
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
                            label: function(context) {
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
    

    // Function to generate distinct colors
    function generateColor(index) {
        const hue = index * 137.508; // use golden angle approximation for distribution
        return `hsla(${hue}, 50%, 60%, 0.2)`;
    }

    $scope.fetchChartData = function () {
        $http.get('api/fetch_database_data', HEADERS)
            .then(function (response) {
                // Assuming response data is in the format: [{endpoint: 'weather.index', size: 1024}, ...]
                $scope.renderChart([
                    { "endpoint": "weather.index", "size": 1024 },
                    { "endpoint": "auth.register", "size": 2048 },
                    { "endpoint": "auth.test1", "size": 2048 },
                    { "endpoint": "auth.test2", "size": 2048 },
                    { "endpoint": "auth.test3", "size": 2048 },
                    { "endpoint": "auth.test4", "size": 2048 },

                ]);
            }, function (errorResponse) {
                console.error('Error fetching chart data:', errorResponse);
            });
    };
    $scope.fetchChartData();







    // Assuming these are the initial configurations, update as necessary
    $scope.cleaningConfig = {};
    $scope.command = '';
    $scope.backupFile = null;

    // Validation for Age of Data
    $scope.isValidAge = function () {
        const age = $scope.cleaningConfig.age;
        return age && age > 0 && age <= 365; // Assuming a valid range is 1 to 365 days
    };

    // Validation for Frequency
    $scope.isValidFrequency = function () {
        const frequency = $scope.cleaningConfig.frequency;
        return frequency && ['daily', 'weekly', 'monthly'].includes(frequency);
    };

    // Modify setupAutomatedCleaning to include validation
    $scope.setupAutomatedCleaning = function () {
        if (!$scope.isValidAge() || !$scope.isValidFrequency()) {
            console.error('Invalid input');
            // Display an error message to the user
            return;
        }
        // Function to handle automated cleaning setup
        $scope.setupAutomatedCleaning = function () {
            $http.post(
                'api/cleaning/setup',
                $.param($scope.cleaningConfig),
                HEADERS
            ).then(function (successResponse) {
                // Handle success
                console.log('Automated cleaning setup successful');
            }, function (errorResponse) {
                console.error('Error setting up automated cleaning:', errorResponse);
            });
        };

        // Function to execute command line operation
        $scope.executeCommandLine = function () {
            $http.post(
                'api/command/execute',
                $.param({ 'command': $scope.command }),
                HEADERS
            ).then(function (successResponse) {
                // Handle command output
                $scope.commandOutput = successResponse.data.output;
            }, function (errorResponse) {
                console.error('Error executing command:', errorResponse);
                $scope.commandOutput = 'Error: Command execution failed';
            });
        };

        // Function to create a backup
        $scope.createBackup = function () {
            $http.post(
                'api/backup/create',
                {}, // Add any necessary parameters
                HEADERS
            ).then(function (successResponse) {
                console.log('Backup created successfully');
            }, function (errorResponse) {
                console.error('Error creating backup:', errorResponse);
            });
        };

        // Function to restore a backup
        $scope.restoreBackup = function () {
            $http.post(
                'api/backup/restore',
                $.param({ 'file': $scope.backupFile }),
                HEADERS
            ).then(function (successResponse) {
                console.log('Backup restored successfully');
            }, function (errorResponse) {
                console.error('Error restoring backup:', errorResponse);
            });
        };
        // Add other necessary functions and service calls as per your application's requirements
    }
}

