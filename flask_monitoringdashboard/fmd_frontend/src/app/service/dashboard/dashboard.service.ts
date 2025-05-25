import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable, of } from 'rxjs';
import { OverviewDto } from './dashboard-defs';
import { AppConfigurationService } from '../app-configuration.service';
import { FmdClientService } from '../FmdClient.service';
@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  constructor(private readonly client: FmdClientService) {}

  public getOverviewData(): Observable<OverviewDto[]> {
    return this.client.get('api/overview');
  }

  public setRule(name: string, value: number): Observable<void> {
    const fd = new FormData();
    fd.append('name', name);
    fd.append('value', value.toString());
    return this.client.post('api/set_rule', fd);
  }
}
