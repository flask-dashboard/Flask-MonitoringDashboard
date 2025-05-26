import { Injectable } from '@angular/core';
import { Observable, of, tap } from 'rxjs';
import { EndpointInfo } from './endpoint-defs';
import { FmdClientService } from '../FmdClient.service';

@Injectable({
  providedIn: 'root',
})
export class EndpointService {
  private endpoints: Map<number, EndpointInfo> = new Map();

  constructor(private readonly client: FmdClientService) {}

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
}
