
import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';
import { NgbCollapse } from '@ng-bootstrap/ng-bootstrap';
import {
  combineLatest,
  filter,
  merge,
  Subject,
  takeUntil,
  tap,
  withLatestFrom,
} from 'rxjs';
import { EndpointContextService } from 'src/app/service/endpoint-context/endpoint-context.service';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import {
  MenuConfig,
  MenuSegmentComponent,
} from './menu-segment/menu-segment.component';

interface MenuState {
  dashboardExpanded: boolean;
  endpointExpanded: boolean;
  configurationExpanded: boolean;
}

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css'],
  imports: [NgbCollapse, FontAwesomeModule, RouterModule],
  standalone: true,
})
export class MenuComponent implements OnInit, OnDestroy {
  public chevronDown = faChevronDown;
  public chevronUp = faChevronUp;
  private destroyed: Subject<void> = new Subject();
  public menuState: MenuState = {
    dashboardExpanded: false,
    endpointExpanded: false,
    configurationExpanded: false,
  };
  public endpoint: EndpointInfo | null = null;

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
    private readonly endpointContext: EndpointContextService
  ) {}

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  ngOnInit() {
    combineLatest([
      this.router.events.pipe(
        filter((event) => event instanceof NavigationEnd)
      ),
      this.endpointContext.endpoint,
    ])
      .pipe(
        takeUntil(this.destroyed),
        tap(([event, endpoint]) => {
          const url = event.urlAfterRedirects || event.url;
          const possibleSegments = url
            .split('/')
            .filter((segment) => segment.length > 0);
          if (possibleSegments.length > 0) {
            const startSegment = possibleSegments[0];

            this.endpoint = endpoint;
            this.menuState = {
              dashboardExpanded: this.overviewConfig
                .map((cfg) => cfg.path)
                .includes(startSegment),
              endpointExpanded: endpoint !== null,
              configurationExpanded: this.configurationConfig
                .map((cfg) => cfg.path)
                .includes(startSegment),
            };
          }
        })
      )
      .subscribe();
  }

  toggleMenuState(item: keyof MenuState): void {
    const state = this.menuState[item];
    this.menuState[item] = !state;
  }
}
