"use strict";

app.directive('pagination', function(){
    return {
        templateUrl: 'static/pages/pagination.html',
        controller: 'PaginationController'
    }
});