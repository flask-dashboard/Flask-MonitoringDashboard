import { CommonModule, NgIf } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router, RouterModule, UrlTree } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';
import { NgbCollapse } from '@ng-bootstrap/ng-bootstrap';
import { filter, map, mergeMap, Subject, takeUntil, tap } from 'rxjs';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { EndpointService } from 'src/app/service/endpoint/endpoint.service';

interface MenuState {
  dashboard: boolean;
  endpoint: boolean;
  configuration: boolean;
}

interface MenuConfig {
  path: string;
  text: string;
}

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css'],
  imports: [NgIf, CommonModule, NgbCollapse, FontAwesomeModule, RouterModule],
  standalone: true,
})
export class MenuComponent implements OnInit, OnDestroy {
  public chevronDown = faChevronDown;
  public chevronUp = faChevronUp;
  private destroyed: Subject<void> = new Subject();
  public menuState: MenuState = {
    dashboard: false,
    endpoint: false,
    configuration: false,
  };
  public endpoint: EndpointInfo | undefined;

  public overviewConfig: MenuConfig[] = [
    { path: 'overview', text: 'Overview' },
    { path: 'hourly_load', text: 'Hourly API Utilization' },
    { path: 'exception_overview', text: 'Exception Monitoring' },
    { path: 'multi_version', text: 'Multi Version API Utilization' },
    { path: 'daily_utilization', text: 'Daily API Utilization' },
    { path: 'api_performance', text: 'API Performance' },
    { path: 'reporting', text: 'Reporting' },
  ];

  public endpointConfig: MenuConfig[] = [
    { path: 'hourly_load', text: 'Hourly API Utilization' },
    { path: 'version_user', text: 'User-Focused Multi-Version Performance' },
    { path: 'version_ip', text: 'IP-Focused Multi-Version Performance' },
    { path: 'versions', text: 'Per-Version Performance' },
    { path: 'users', text: 'Per-User Performance' },
    { path: 'profiler', text: 'Profiler' },
    { path: 'grouped-profiler', text: 'Grouped Profiler' },
    { path: 'exceptions', text: 'Exceptions' },
    { path: 'outliers', text: 'Outliers' },
    { path: 'status_code_distribution', text: 'Status Code Distribution' },
  ];

  public configurationConfig: MenuConfig[] = [
    { path: 'configuration', text: 'General Settings' },
    { path: 'database_management', text: 'Database Management' },
  ];

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
        tap((event) => {
          const url = event.urlAfterRedirects || event.url;
          console.log(url);
          const possibleSegments = url
            .split('/')
            .filter((segment) => segment.length > 0);
          if (possibleSegments.length > 0) {
            const startSegment = possibleSegments[0];

            this.endpoint =
              possibleSegments[0] !== 'endpoint' ? undefined : this.endpoint;
            this.menuState = {
              dashboard: this.overviewConfig
                .map((cfg) => cfg.path)
                .includes(startSegment),
              endpoint: possibleSegments[0] === 'endpoint',
              configuration: this.configurationConfig
                .map((cfg) => cfg.path)
                .includes(startSegment),
            };
          }
        }),
        map(() => this.router.routerState.root),
        map((route) => {
          while (route.firstChild) {
            route = route.firstChild;
          }
          return route;
        }),
        filter((route) => route.outlet === 'primary'),
        map((route) => Number(route.snapshot.params['id'])),
        filter((id) => !isNaN(id) && id !== this.endpoint?.id),
        mergeMap((id) => this.endpointService.getEndpointInfo(id))
      )
      .subscribe((endpoint) => {
        console.log('hit');
        this.endpoint = endpoint;
      });
  }

  toggleMenuState(item: keyof MenuState): void {
    const state = this.menuState[item];
    this.menuState[item] = !state;
  }
}
