import { coerceString } from "plotly.js-cartesian-dist";

export function ExceptionController($scope, $http, $location, menuService, paginationService, endpointService) {
    endpointService.reset();
    menuService.reset('exception_overview'); 
    const queryables = ['message', 'type', 'endpoint', 'genericSearch']

    $scope.table = [];

    const handleKeyDown = function (key) {
        if(key.key === "Enter") {
            $scope.query();
        }
    }

    const removeUnwelcomeParameters = function () {
        const params = $location.search();
        Object.keys(params).forEach(key => {
            if (!queryables.includes(key)) $location.search(key, null);
        });
    }

    const getQueryString = function () {
        removeUnwelcomeParameters();
        let query = decodeURI(window.location.search);
        if (query.includes("?")){
            query = query.slice(1);
        }
        if (query.includes("genericSearch=")){
            const parameters = query.split("&");
            query = findValueInArray("genericSearch", parameters);
        }
        return query;
    }

    $scope.queryString = getQueryString();
    $scope.oldQuery = $scope.queryString;

    document.addEventListener("keydown", handleKeyDown, false);

    $scope.$on('$destroy', function() {
        document.removeEventListener('keydown', handleKeyDown, false);
    });

    paginationService.init('exceptions');
    $http.get('api/num_exceptions'+window.location.search).then(function (response) {
        paginationService.setTotal(response.data);
    });

    $scope.getEndpoint = function () {
        return 'api/exception_info/' + paginationService.getLeft() + '/' + paginationService.perPage;
    }

    function findValueInArray(key, arr){
        for (let i = 0; i < arr.length; i++){
            const currentParam = arr[i].split('=');
            if (currentParam.length > 0 && currentParam[0] === key) return currentParam[1];
        }
    }

    $scope.buildQueryString = function (queryString){
        if (queryString === "" || queryString === undefined || queryString === null) {
            $location.search("genericSearch", null);
            return;
        }
        let isGenericSearch = true;
        const parameters = queryString.split("&");
        queryables.forEach((queryable, _) => {
            if (queryString.includes(queryable+"=")){
                isGenericSearch = false;
                const val = findValueInArray(queryable, parameters);
                $location.search(queryable, val);
            } else {
                $location.search(queryable, null);
            }
        });
        if (isGenericSearch) $location.search("genericSearch", queryString);
        else $location.search("genericSearch", null);
    }

    $scope.query = function (){
        if ($scope.queryString === $scope.oldQuery) return;
        $scope.buildQueryString($scope.queryString);
        paginationService.onReload();
    }

    paginationService.onReload = function () {
        $http.get($scope.getEndpoint()+window.location.search).then(function (response) {
            $scope.table = response.data;
        });
        $http.get('api/num_exceptions'+window.location.search).then(function (response) {
            paginationService.total = response.data;
        });
    };
};
