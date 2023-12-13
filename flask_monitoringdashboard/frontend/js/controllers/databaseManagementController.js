export function DatabaseManagementController($scope, $http, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('database_management');

    $scope.databaseSize = 'N/A';

    $scope.getDatabaseSize = function () {
        $http.get('/dashboard/database_pruning/get_database_size')
            .then(function (response) {
                $scope.databaseSize = response.data.size;
            }, function (error) {
                console.error('Error fetching database size:', error.data);
            });
    };

    $scope.getDatabaseSize();


    // Initialize the configuration for pruning
    $scope.pruneOnDemandConfig = {
        ageThresholdWeeks: 1, // Default value or null if you prefer no default
        deleteCustomGraphData: false
    };

    // Variables for feedback messages
    $scope.pruneOnDemandMessage = '';
    $scope.pruneOnDemandIsSuccess = false;

    $scope.pageSize = '10';

    // Function to prune the database
    $scope.pruneDatabase = function () {
        let weekOrWeeks = $scope.pruneOnDemandConfig.ageThresholdWeeks === 1 ? ' week' : ' weeks';
        let confirmationMessage = 'Are you sure you want to prune all request data older than '
            + $scope.pruneOnDemandConfig.ageThresholdWeeks + weekOrWeeks + '?';
        if (!confirm(confirmationMessage)) {
            return; // Stop the function if the user clicks 'Cancel'
        }

        // Confirmation dialog
        const pruneData = {
            age_threshold_weeks: $scope.pruneOnDemandConfig.ageThresholdWeeks,
            delete_custom_graph_data: $scope.pruneOnDemandConfig.deleteCustomGraphData
        };

        $http.post('/dashboard/database_pruning/prune_on_demand', pruneData)
            .then(function (response) {
                $scope.pruneOnDemandIsSuccess = true;
                $scope.pruneOnDemandMessage = 'Database pruning complete.';
            }, function (error) {
                $scope.pruneOnDemandIsSuccess = false;
                $scope.pruneOnDemandMessage = 'Error pruning database: ' + (error.data.error || 'Unknown error');
            });
    };

    // Function to fetch the pruning schedule
    $scope.getPruningSchedule = function () {
        $http.get('/dashboard/database_pruning/get_pruning_schedule')
            .then(function (response) {
                $scope.pruningSchedule = response.data;
            }, function (error) {
            });
    };
    $scope.getPruningSchedule();
}
