import { Injectable } from '@angular/core';
import { FmdClientService } from '../FmdClient.service';
import {
  DateInterval,
  DateIntervalToTimestampInterval,
  Summary,
} from './reporting-defs';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ReportingService {
  constructor(private readonly client: FmdClientService) {}

  createReportFromIntervals(
    interval: DateInterval,
    baselineInterval: DateInterval,
    milliConv?: boolean
  ): Observable<Summary[]> {
    return this.client.post('api/reporting/make_report/intervals', {
      interval: DateIntervalToTimestampInterval(interval, milliConv),
      baseline_interval: DateIntervalToTimestampInterval(
        baselineInterval,
        milliConv
      ),
    });
  }

  createReportFromCommits(
    commitVersion: string,
    baselineCommitVersion: string
  ): Observable<Summary[]> {
    return this.client.post('api/reporting/make_report/commits', {
      commit_version: commitVersion,
      baseline_commit_version: baselineCommitVersion,
    });
  }
}
