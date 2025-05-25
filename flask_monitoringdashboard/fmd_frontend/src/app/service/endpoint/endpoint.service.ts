import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { EndpointInfo } from './endpoint-defs';
import { FmdClientService } from '../FmdClient.service';

@Injectable({
  providedIn: 'root',
})
export class EndpointService {
  constructor(private readonly client: FmdClientService) {}

  getEndpointInfo(id: number): Observable<EndpointInfo> {
    return this.client.get('/api/endpoint_info/' + id);
  }
}
