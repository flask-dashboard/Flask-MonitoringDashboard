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

        var dashboardPages = ['overview', 'hourly_load', 'multi_version', 'daily_load', 'api_performance', 'reporting'];

        if (dashboardPages.includes(page)) {
            $('#collapseDashboard').collapse('show');
        } else {
            $('#collapseDashboard').collapse('hide');
        }

        var endpointPages = [
            'endpoint_hourly', 'endpoint_user_version', 'endpoint_ip', 'endpoint_version', 'endpoint_user',
            'endpoint_profiler', 'endpoint_grouped_profiler', 'endpoint_outlier', 'status_code_distribution'
        ];

        if (endpointPages.includes(page)) {
            $('#collapseEndpoint').collapse('show');
        } else {
            $('#collapseEndpoint').collapse('hide');
        }
    }
});