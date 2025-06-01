import { Observable } from 'rxjs';
import { FmdClientService } from './../FmdClient.service';
import { Injectable } from '@angular/core';
import { HourlyLoad, RequestsData } from './request-defs';
import { TimeMachineService } from '../time-machine.service';

@Injectable({
  providedIn: 'root',
})
export class RequestService {
  constructor(
    private readonly client: FmdClientService,
    private readonly time: TimeMachineService
  ) {}

  getRequests(startDate: Date, endDate: Date): Observable<RequestsData> {
    return this.client.get(
      `api/requests/${this.time.format(startDate)}/${this.time.format(endDate)}`
    );
  }

  getHourlyLoad(
    startDate: Date,
    endDate: Date,
    id?: number
  ): Observable<HourlyLoad> {
    return this.client.get(
      `api/hourly_load/${this.time.format(startDate)}/${this.time.format(
        endDate
      )}${id ? '/' + id : ''}`
    );
  }
}
