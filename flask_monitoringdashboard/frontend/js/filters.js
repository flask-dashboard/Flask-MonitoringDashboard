export function applyFilters(app) {

    app.filter('duration_ms', function () {
        return function (time) {
            return Math.round(parseFloat(time) * 10) / 10;
        }
    });

    app.filter('duration', function () {
        return function (time) {
            let ms = Math.round(parseFloat(time) * 10) / 10;
            let s = ms / 1000;
            let min = Math.floor(s / 60);
            let hr = Math.floor(s / 3600);
            let day = Math.floor(hr / 24);
            let value = "";
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
    });

// to parse the date and reformat

    app.filter('dateLayout', function () {
        return date => {
            let d = new Date(date);
            return ("0" + d.getDate()).slice(-2) + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" +
                d.getFullYear() + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
        }
    });


    app.filter('dateShort', function () {
        return date => {
            let monthNames = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ];
            let d = new Date(date);
            let day = d.getDate();
            let monthIndex = d.getMonth();
            let year = d.getFullYear();

            return monthNames[monthIndex] + ' ' + day + ', ' + year;
        }
    });


    app.filter('dateDifference', function () {

        return function (date) {
            if (date === null) {
                return '';
            }

            let utc = new Date().getTime();
            let parsed = Date.parse(date);
            let diff = utc - parsed;

            let sec = Math.round(diff / 1000);
            let min = Math.round(sec / 60);
            let hour = Math.round(min / 60);
            let day = Math.round(hour / 24);
            let week = Math.round(day / 7);
            let month = Math.round(day / 30);
            let year = Math.round(day / 365);

            function s(number) {
                if (number !== 1) {
                    return "s";
                }
                return "";
            }

            if (sec < 60) {
                return sec + " second" + s(sec) + " ago";
            } else if (min < 60) {
                return min + " minute" + s(min) + " ago";
            } else if (hour < 24) {
                return hour + " hour" + s(hour) + " ago";
            } else if (day < 7) {
                return day + " day" + s(day) + " ago";
            } else if (week < 5) {
                return week + " week" + s(week) + " ago";
            } else if (month < 12) {
                return month + " month" + s(month) + " ago";
            }
            return year + " year" + s(year) + " ago";
        }
    });

    app.filter('abs', function () {
        return function (num) {
            return Math.abs(num);
        }
    });
}