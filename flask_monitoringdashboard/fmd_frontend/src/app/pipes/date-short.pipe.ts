import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'date-short',
  standalone: false,
})
export class DateShortPipe implements PipeTransform {
  transform(date: Date | string): string {
    const monthNames = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    const d = new Date(date);
    const day = d.getDate();
    const monthIndex = d.getMonth();
    const year = d.getFullYear();

    return monthNames[monthIndex] + ' ' + day + ', ' + year;
  }
}
