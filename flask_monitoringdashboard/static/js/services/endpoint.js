app.service('endpointService', function ($http, $routeParams) {
    let that = this;
    this.info = {
        id: 0,
        endpoint: ''
    };

    this.getInfo = function () {
        return this.info;
    };

    this.reset = function () {
        if (typeof $routeParams.endpointId !== 'undefined') {
            this.info.id = $routeParams.endpointId;
            this.getInfo();
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
});