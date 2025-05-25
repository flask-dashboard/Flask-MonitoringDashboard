import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter, map, mergeMap, Subject, takeUntil } from 'rxjs';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { EndpointService } from 'src/app/service/endpoint/endpoint.service';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css'],
})
export class MenuComponent implements OnInit, OnDestroy {
  private destroyed: Subject<void> = new Subject();
  public endpoint: EndpointInfo | undefined;
  constructor(
    private readonly router: Router,
    private readonly endpointService: EndpointService
  ) {}

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  ngOnInit() {
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
        mergeMap((id) => this.endpointService.getEndpointInfo(id))
      )
      .subscribe((endpoint) => {
        this.endpoint = endpoint;
      });
  }
}
