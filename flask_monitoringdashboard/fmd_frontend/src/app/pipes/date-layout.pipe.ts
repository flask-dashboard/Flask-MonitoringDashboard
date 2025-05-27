import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'date-layout',
})
export class DateLayoutPipe implements PipeTransform {
  transform(date: Date | string): any {
    let d = new Date(date);
    return (
      ('0' + d.getDate()).slice(-2) +
      '-' +
      ('0' + (d.getMonth() + 1)).slice(-2) +
      '-' +
      d.getFullYear() +
      ' ' +
      ('0' + d.getHours()).slice(-2) +
      ':' +
      ('0' + d.getMinutes()).slice(-2)
    );
  }
}
