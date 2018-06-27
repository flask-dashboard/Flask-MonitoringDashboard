
function format_time(time){
    // ms is a float or int
    //ms = Math.round(parseFloat(ms) / 10) * 10;
    var ms = Math.round(parseFloat(time) * 10) / 10;
    var s = ms / 1000;
    var min = Math.floor(s / 60);
    var hr = Math.floor(s / 3600);
    var day = Math.floor(hr / 24);
    var value = "";
    if (ms < 100.5) {
        value = ms + " ms";
    } else if (ms < 999.5) {
        value = Math.round(ms) + " ms";
    } else if (s < 60) {
        s = Math.round(ms / 100) / 10;
        value = s + " sec";
    } else if (hr === 0) {
        s = Math.round(s % 60);
        value = min + " min";
        if (s > 0) {
            value += ", " + s + " sec";
        }
    } else if (day === 0) {
        value = hr + " hr";
        min = Math.round(min % 60);
        if (min > 0) {
            value += ", " + min + " min";
        }
    } else {
        value = day + " d";
        hr = Math.round(hr % 24);
        if (hr > 0) {
            value += ", " + hr + " hr";
        }
    }
    return value;
}

function format_date(date){
    if (date === "" || date.substr(date.length - 3) === "ago"){
        return date;
    }

    var utc = new Date().getTime();
    var parsed = new Date(date.replace(" ", "T")+"Z");
    var diff = utc - parsed;

    var sec = Math.round(diff / 1000);
    var min = Math.round(sec / 60);
    var hour = Math.round(min / 60);
    var day = Math.round(hour / 24);
    var week = Math.round(day / 7);
    var month = Math.round(day / 30);
    var year = Math.round(day / 365);

    function s(number){
        if (number !== 1){
            return "s";
        }
        return "";
    }

    if (sec < 60){
        return sec + " second" + s(sec) + " ago";
    } else if (min < 60){
        return min + " minute" + s(min) + " ago";
    } else if (hour < 24){
        return hour + " hour" + s(hour) + " ago";
    } else if (day < 7){
        return day + " day" + s(day) + " ago";
    } else if (week < 5){
        return week + " week" + s(week) + " ago";
    } else if (month < 12){
        return month + " month" + s(month) + " ago";
    }
    return year + " year" + s(year) + " ago";
}