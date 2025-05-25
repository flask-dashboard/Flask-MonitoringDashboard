import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'dateDifference',
    standalone: false
})
export class DateDifferencePipe implements PipeTransform {
  transform(date: string): any {
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

    function s(number: number) {
      if (number !== 1) {
        return 's';
      }
      return '';
    }

    if (sec < 60) {
      return sec + ' second' + s(sec) + ' ago';
    } else if (min < 60) {
      return min + ' minute' + s(min) + ' ago';
    } else if (hour < 24) {
      return hour + ' hour' + s(hour) + ' ago';
    } else if (day < 7) {
      return day + ' day' + s(day) + ' ago';
    } else if (week < 5) {
      return week + ' week' + s(week) + ' ago';
    } else if (month < 12) {
      return month + ' month' + s(month) + ' ago';
    }
    return year + ' year' + s(year) + ' ago';
  }
}
