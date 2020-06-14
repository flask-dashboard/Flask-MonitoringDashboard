export default function () {
    this.title = '';
    this.content = '';
    this.user = '';

    this.configure = function(title, content){
        this.title = title;
        this.content = content;
        console.log("Check - " + this.name);
    }
}