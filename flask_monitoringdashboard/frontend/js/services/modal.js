export default function () {
    this.action = {};
    this.error = {};

    this.setConfirm = function(name, action){
        this.action[name] = action;
    }

    this.setErrorMessage = function(name, message){
        this.error[name] = message;
    }

    this.confirm = function(name){
        this.action[name]();
    }
}