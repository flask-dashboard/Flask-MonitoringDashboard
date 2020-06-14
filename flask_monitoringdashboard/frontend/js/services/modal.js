export default function () {
    this.action = {};
    this.error = {};
    this.textButtonYes = {};
    this.textButtonNo = {};

    this.setConfirm = function(name, action){
        this.action[name] = action;
    }

    this.getTextButtonYes = function(name){
        return this.textButtonYes[name] || "Yes";
    }

    this.getTextButtonNo = function(name){
        return this.textButtonNo[name] || "No";
    }

    this.setErrorMessage = function(name, message){
        this.error[name] = message;
    }

    this.confirm = function(name){
        this.action[name]();
    }
}