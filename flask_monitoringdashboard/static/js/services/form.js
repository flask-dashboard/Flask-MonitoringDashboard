
app.service('formService', function ($http, endpointService) {
    let that = this;

    this.dateFields = [];
    this.multiFields = [];

    this.clear = function () {
        that.multiFields = [];
        that.dateFields = [];
    };

    function addMultiSelect(name) {
        let obj = {
            'name': name,
            'values': [],
            'selected': [], // subset of 'items'
            'initialized': false
        };
        that.multiFields.push(obj);
        return obj;
    }

    this.initialize = function (obj) {
        obj.initialized = true;
        if (that.multiFields.every(o => o.initialized)) {
            that.reload();
        }
    };

    this.getMultiSelection = function (name) {
        return that.multiFields.find(o => o.name == name).selected;
    };

    this.addDate = function (name) {
        let obj = {
            'name': name,
            'value': new Date(),
        };
        that.dateFields.push(obj);
        return obj;
    };

    this.getDate = function (name) {
        return parseDate(that.dateFields.find(o => o.name == name).value);
    };

    this.addVersions = function (endpoint_id) {
        let obj = addMultiSelect('versions');
        let url = 'api/versions';
        if (typeof endpoint_id !== "undefined") {
            url += '/' + endpoint_id;
        }
        $http.get(url).then(function (response) {
            obj.values = response.data;
            obj.selected = response.data.slice(-10);
            that.initialize(obj);
        });
    };

    this.addEndpoints = function () {
        let obj = addMultiSelect('endpoints');
        $http.get('api/endpoints').then(function (response) {
            obj.values = response.data.map(d => d.name);
            obj.selected = obj.values;
            that.initialize(obj);
        });
    };

    this.addUsers = function () {
        let obj = addMultiSelect('users');
        $http.get('api/users/' + endpointService.info.id).then(function (response) {
            obj.values = response.data;
            obj.selected = obj.values;
            that.initialize(obj);
        });
    };

    this.addIP = function () {
        let obj = addMultiSelect('IP-addresses');
        $http.get('api/ip/' + endpointService.info.id).then(function (response) {
            obj.values = response.data;
            obj.selected = obj.values;
            that.initialize(obj);
        });
    };

    let parseDate = function (date) {
        return date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2)
            + "-" + ("0" + date.getDate()).slice(-2);
    };

    this.reload = function () {
    };
    this.setReload = function (f) {
        this.reload = f;
    }
});