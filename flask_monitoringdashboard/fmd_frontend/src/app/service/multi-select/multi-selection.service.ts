import { MultiSelect } from 'src/app/shared/plotly/plotly.component';
import { inject, Injectable } from '@angular/core';
import { filter, map, mergeMap, Observable, take } from 'rxjs';
import { DateLayoutPipe } from 'src/app/pipes/date-layout.pipe';
import { VersionService } from '../version/version.service';
import { EndpointService } from '../endpoint/endpoint.service';
import { EndpointContextService } from '../endpoint-context/endpoint-context.service';
import { Hit } from '../endpoint/endpoint-defs';

@Injectable({
  providedIn: 'root',
})
export class MultiSelectionService {
  private readonly dateLayout = inject(DateLayoutPipe)
  private readonly version = inject(VersionService)
  private readonly endpoint = inject(EndpointService)
  private readonly endpointContext = inject(EndpointContextService)

  private getMs(name: string): MultiSelect {
    return {
      name,
      values: [],
      selected: [],
    };
  }

  private HitsToMs(hits: Hit[], name: string): MultiSelect {
    const ms = this.getMs(name);
    ms.values = hits.map((hit) => ({
      id: hit.name,
      text: hit.name + ' : ' + hit.hits + ' requests',
    }));

    ms.selected = ms.values.slice(0, this.DEFAULT_SELECTED);
    return ms;
  }

  private readonly DEFAULT_SELECTED = 10;

  getVersions(): Observable<MultiSelect> {
    const ms = this.getMs('versions');
    return this.version.getVersions().pipe(
      map((versions) => {
        ms.values = versions.map((version) => ({
          id: version.version,
          text:
            version.version + ' : ' + this.dateLayout.transform(version.date),
        }));
        ms.selected = ms.values.slice(-this.DEFAULT_SELECTED);
        return ms;
      })
    );
  }

  getEndpoints(): Observable<MultiSelect> {
    return this.endpoint
      .getEndpointsHits()
      .pipe(map((hits) => this.HitsToMs(hits, 'endpoints')));
  }

  getUsers(): Observable<MultiSelect> {
    return this.endpointContext.endpoint.pipe(
      take(1),
      filter((endpoint) => endpoint !== null),
      mergeMap((endpoint) => this.endpoint.getUserHits(endpoint.id)),
      map((hits) => this.HitsToMs(hits, 'users'))
    );
  }

  getIPAddresses(): Observable<MultiSelect> {
    return this.endpointContext.endpoint.pipe(
      take(1),
      filter((endpoint) => endpoint !== null),
      mergeMap((endpoint) => this.endpoint.getIPHits(endpoint.id)),
      map((hits) => this.HitsToMs(hits, 'IP-addresses'))
    );
  }
}
