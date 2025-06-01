import { Injectable } from '@angular/core';
import moment, { DurationInputArg1, DurationInputArg2, Moment } from 'moment';
import { ReportInterval } from './reporting/reporting-defs';

@Injectable({
  providedIn: 'root',
})
export class TimeMachineService {
  constructor() {}

  now(): Moment {
    return moment();
  }

  fnow(
    format?: string,
    amnt?: DurationInputArg1,
    type?: DurationInputArg2
  ): string {
    if (amnt && type) {
      return this.now().subtract(amnt, type).format(format);
    }

    return this.now().format(format);
  }

  format(date: Date | Moment, format: string = 'yyyy-MM-DD'): string {
    const mom = moment(date);
    return mom.format(format);
  }

  intervals(amnt: DurationInputArg1, type: DurationInputArg2): ReportInterval {
    const t1 = moment().subtract(amnt, type).startOf(type);

    const t2 = moment().subtract(amnt, type).endOf(type);
    const t3 = moment().startOf(type);
    const t4 = moment().endOf(type);

    return {
      comparison: {
        from: t3.toDate(),
        to: t4.toDate(),
      },
      baseline: {
        from: t1.toDate(),
        to: t2.toDate(),
      },
    };
  }
}
