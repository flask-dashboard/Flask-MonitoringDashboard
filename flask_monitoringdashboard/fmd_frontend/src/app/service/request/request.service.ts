import { Observable } from 'rxjs';
import { FmdClientService } from './../FmdClient.service';
import { Injectable } from '@angular/core';
import { HourlyLoad, RequestsData } from './request-defs';
import { formatDate } from '@angular/common';

@Injectable({
  providedIn: 'root',
})
export class RequestService {
  private formatDate = (date: Date): string =>
    formatDate(date, 'yyyy-MM-dd', navigator.language);

  constructor(private readonly client: FmdClientService) {}

  getRequests(startDate: Date, endDate: Date): Observable<RequestsData> {
    return this.client.get(
      `api/requests/${this.formatDate(startDate)}/${this.formatDate(endDate)}`
    );
  }

  getHourlyLoad(
    startDate: Date,
    endDate: Date,
    id?: number
  ): Observable<HourlyLoad> {
    return this.client.get(
      `api/hourly_load/${this.formatDate(startDate)}/${this.formatDate(
        endDate
      )}${id ? '/' + id : ''}`
    );
  }
}
