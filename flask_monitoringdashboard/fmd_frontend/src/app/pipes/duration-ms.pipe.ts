import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'durationMs',
})
export class DurationMsPipe implements PipeTransform {
  transform(time: number): number {
    return Math.round(time * 10) / 10;
  }
}
