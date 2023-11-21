const HEADERS = {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
    }
};

export function DatabaseManagementController($scope, $http, menuService, endpointService, modalService) {
    endpointService.reset();
    menuService.reset('database_management');

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