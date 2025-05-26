import { Injectable, OnDestroy } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import {
  BehaviorSubject,
  filter,
  map,
  mergeMap,
  Observable,
  of,
  Subject,
  takeUntil,
} from 'rxjs';
import { EndpointInfo } from '../endpoint/endpoint-defs';
import { EndpointService } from '../endpoint/endpoint.service';

@Injectable({
  providedIn: 'root',
})
export class EndpointContextService implements OnDestroy {
  private destroyed = new Subject<void>();
  private _endpointSubject = new BehaviorSubject<EndpointInfo | null>(null);
  constructor(
    private readonly router: Router,
    private readonly endpointService: EndpointService
  ) {
    this.router.events
      .pipe(
        takeUntil(this.destroyed),
        filter((event) => event instanceof NavigationEnd),
        map(() => this.router.routerState.root),
        map((route) => {
          while (route.firstChild) {
            route = route.firstChild;
          }
          return route;
        }),
        filter((route) => route.outlet === 'primary'),
        map((route) => Number(route.snapshot.params['id'])),
        mergeMap((id) =>
          isNaN(id) ? of(null) : this.endpointService.getEndpointInfo(id)
        )
      )
      .subscribe((endpoint) => {
        this._endpointSubject.next(endpoint);
      });
  }

  public get endpoint(): Observable<EndpointInfo | null> {
    return this._endpointSubject.asObservable();
  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
    this._endpointSubject.complete();
  }
}
