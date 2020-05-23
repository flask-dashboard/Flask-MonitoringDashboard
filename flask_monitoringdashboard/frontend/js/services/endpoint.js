export default function ($http, $routeParams) {
    let that = this;
    this.info = {
        id: 0,
        endpoint: ''
    };
    this.graphId = 0;

    this.customGraphs = [];
    this.getGraph = function () {
        return this.customGraphs.find(o => o.graph_id === that.graphId);
    };

    this.getGraphTitle = function () {
        let graph = this.getGraph();
        if (typeof graph !== 'undefined') {
            return graph.title;
        }
        return '';
    };

    $http.get('api/custom_graphs').then(function (response) {
        that.customGraphs = response.data;
        if (that.graphId !== 0) {
            that.onNameChanged(that.getGraphTitle())
        }
    });

    this.reset = function () {
        if (typeof $routeParams.endpointId !== 'undefined') {
            this.info.id = $routeParams.endpointId;
            this.getInfo();
        } else if (typeof $routeParams.graphId !== 'undefined') {
            this.graphId = $routeParams.graphId;
        } else {
            this.info.id = 0;
        }
    };

    this.onNameChanged = function (name) {
    };

    this.getInfo = function () {
        $http.get('api/endpoint_info/' + this.info.id).then(function (response) {
            that.info = response.data;
            that.onNameChanged(that.info.endpoint);
        });
    };
};