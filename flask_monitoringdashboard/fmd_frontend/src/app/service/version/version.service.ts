import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { EndpointUserVersion, EndpointVersion } from './version-defs';
import { FmdClientService } from '../FmdClient.service';
import { MultiSelect } from 'src/app/shared/plotly/plotly.component';
import { version } from 'moment';

@Injectable({
  providedIn: 'root',
})
export class VersionService {
  constructor(private readonly client: FmdClientService) { }

  getVersions(): Observable<EndpointVersion[]> {
    return this.client.get('api/versions');
  }

  getMultiVersionUtilization(
    endpoints: MultiSelect,
    versions: MultiSelect
  ): Observable<number[][]> {
    return this.client.post('api/multi_version', {
      data: {
        versions: versions.selected.map((sel) => sel.id),
        endpoints: endpoints.selected.map((sel) => sel.id),
      },
    });
  }

  getVersionUserUtilization(
    users: MultiSelect,
    versions: MultiSelect,
    id: number
  ): Observable<EndpointUserVersion> {
    return this.client.post('api/version_user/' + id, {
      data: {
        users: users.selected.map((sel) => sel.id),
        versions: versions.selected.map((sel) => sel.text),
      },
    });
  }
}
