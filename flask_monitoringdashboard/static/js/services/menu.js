app.service('menuService', function ($http, endpointService) {
    this.page = '';
    this.endpoint = endpointService;

    this.reset = function (page) {
        if (this.page !== page) {
            this.page = page;
        }
        if (page.substr(0, 'custom_graph'.length) === 'custom_graph') {
            $('#collapseCustomGraphs').collapse('show');
        } else {
            $('#collapseCustomGraphs').collapse('hide');
        }

        if (page === 'overview' || page === 'hourly_load' || page === 'multi_version' ||
            page === 'daily_load' || page === 'api_performance') {
            $('#collapseDashboard').collapse('show');
        } else {
            $('#collapseDashboard').collapse('hide');
        }

        if (page === 'endpoint_hourly' || page === 'endpoint_user_version' || page === 'endpoint_ip' ||
            page === 'endpoint_version' || page === 'endpoint_user' || page === 'endpoint_profiler' ||
            page === 'endpoint_grouped_profiler' || page === 'endpoint_outlier') {
            $('#collapseEndpoint').collapse('show');
        } else {
            $('#collapseEndpoint').collapse('hide');
        }
    }
});