import { inject, Injectable } from '@angular/core';
import { Observable, of, tap } from 'rxjs';
import { Hit, EndpointInfo, ApiPerformance, VersionIpData } from './endpoint-defs';
import { FmdClientService } from '../FmdClient.service';
import { MultiSelect } from 'src/app/shared/plotly/plotly.component';

@Injectable({
  providedIn: 'root',
})
export class EndpointService {
  private endpoints: Map<number, EndpointInfo> = new Map();
  private readonly client = inject(FmdClientService)

  getEndpointInfo(id: number): Observable<EndpointInfo> {
    return this.client.get<EndpointInfo>('/api/endpoint_info/' + id);
  }

  getCachedEndpointInfo(id: number): Observable<EndpointInfo> {
    const cached = this.endpoints.get(id);
    if (cached) return of(cached);

    return this.client
      .get<EndpointInfo>('/api/endpoint_info/' + id)
      .pipe(tap((endpoint) => this.endpoints.set(id, endpoint)));
  }

  getEndpointsHits(): Observable<Hit[]> {
    return this.client.get('api/endpoints_hits');
  }

  getUserHits(id: number): Observable<Hit[]> {
    return this.client.get('api/users/' + id);
  }

  getIPHits(id: number): Observable<Hit[]> {
    return this.client.get('api/users/' + id);
  }

  getApiPerformance(endpoints: MultiSelect): Observable<ApiPerformance[]> {
    return this.client.post('api/api_performance', {
      data: { endpoints: endpoints.selected.map((sel) => sel.id) },
    });
  }

  getVersionIp(id: number, versions: string[], ip: string[]): Observable<VersionIpData> {
    return this.client.post(`api/version_ip/${id}`, {
      data: { versions, ip }
    });
  }
}
