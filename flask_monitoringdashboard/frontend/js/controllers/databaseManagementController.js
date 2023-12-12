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
        deleteCustomGraphs: false
    };

    // Variables for feedback messages
    $scope.pruneOnDemandMessage = '';
    $scope.pruneOnDemandIsSuccess = false;

    $scope.pageSize = '10';

    // Function to prune the database
    $scope.pruneDatabase = function () {
        const pruneData = {
            age_threshold_weeks: $scope.pruneOnDemandConfig.ageThresholdWeeks,
            delete_custom_graphs: $scope.pruneOnDemandConfig.deleteCustomGraphs
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
                console.error('Error fetching pruning schedule:', error.data);
            });
    };
    $scope.getPruningSchedule();
}
