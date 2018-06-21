
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