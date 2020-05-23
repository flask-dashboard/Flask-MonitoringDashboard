export default function formService($http, endpointService, $filter) {
    const SLICE = 10;

    let that = this;

    this.dateFields = [];
    this.multiFields = [];
    this.isLoading = true;

    this.clear = function () {
        that.multiFields = [];
        that.dateFields = [];
    };

    function addMultiSelect(name) {
        let obj = {
            'name': name,
            'values': [], // list of {id: , text: }
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

        return that.multiFields.find(o => o.name == name).selected.map(d => d.id);
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
            obj.values = response.data.map(d => {
                    return {
                        id: d.version,
                        text: d.version + ' : ' + $filter('dateLayout')(d.date)
                    }
                }
            );
            obj.selected = obj.values.slice(-SLICE);
            that.initialize(obj);
        });
    };

    this.addEndpoints = function () {
        let obj = addMultiSelect('endpoints');
        $http.get('api/endpoints_hits').then(function (response) {
            obj.values = response.data.map(d => {
                return {
                    id: d.name,
                    text: d.name + ' : ' + d.hits + ' requests'
                }
            });
            obj.selected = obj.values.slice(0, SLICE);
            that.initialize(obj);
        });
    };

    this.addUsers = function () {
        let obj = addMultiSelect('users');
        $http.get('api/users/' + endpointService.info.id).then(function (response) {
            obj.values = response.data.map(d => {
                return {
                    id: d.user,
                    text: d.user + ' : ' + d.hits + ' requests'
                }
            });
            obj.selected = obj.values.slice(0, SLICE);
            that.initialize(obj);
        });
    };

    this.addIP = function () {
        let obj = addMultiSelect('IP-addresses');
        $http.get('api/ip/' + endpointService.info.id).then(function (response) {
            obj.values = response.data.map(d => {
                return {
                    id: d.ip,
                    text: d.ip + ' : ' + d.hits + ' requests'
                }
            });
            obj.selected = obj.values.slice(0, SLICE);
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
        this.reload = function () {
            that.isLoading = true;
            f();
        };
    }
}
