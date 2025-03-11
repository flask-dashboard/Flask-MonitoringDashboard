export function ExceptionController($scope, $http, $location, menuService, paginationService, endpointService) {
    endpointService.reset();
    menuService.reset('exception_overview'); 
    paginationService.init('exceptions');
    const queryables = ['message', 'type', 'endpoint', 'genericSearch']

    $scope.table = [];

    const getQueryString = function () {
        const params = new URLSearchParams(window.location.search);
        
        for (const key of params.keys()) { // remove keys from URL that aren't queryables
            if (!queryables.includes(key)) {
                $location.search(key, null);
            }
        }

        return params.has("genericSearch") ? params.get("genericSearch") : params.toString();
    };

    $scope.queryString = getQueryString();
    $scope.oldQuery = $scope.queryString;

    const setPaginationTotal = function() {
        $http.get('api/num_exceptions'+window.location.search).then(function (response) {
            paginationService.setTotal(response.data);
        });
    }
    setPaginationTotal();
    
    function buildQueryString(queryString) {
        if (!queryString) {
            $location.search("genericSearch", null);
            return;
        }

        const queryParams = new URLSearchParams(queryString);
        let isGenericSearch = true;
    
        queryables.forEach(queryable => {
            if (queryParams.has(queryable)) {
                isGenericSearch = false;
                $location.search(queryable, queryParams.get(queryable));
            } else {
                $location.search(queryable, null);
            }
        });
    
        $location.search("genericSearch", isGenericSearch ? queryString : null);
    };

    paginationService.onReload = function () {
        const endpoint = 'api/exception_info/' + paginationService.getLeft() + '/' + paginationService.perPage;
        $http.get(endpoint+window.location.search).then(function (response) {
            $scope.table = response.data;
        });
    };

    const handleKeyDown = function (key) {
        if(key.key === "Enter") {
            if ($scope.queryString === $scope.oldQuery) return;
            buildQueryString($scope.queryString);
            setPaginationTotal();
        }
    }

    document.addEventListener("keydown", handleKeyDown, false);

    $scope.$on('$destroy', function() {
        document.removeEventListener('keydown', handleKeyDown, false);
    });
};
