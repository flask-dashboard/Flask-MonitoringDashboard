import { HourlyLoadComponent } from './endpoint/hourly-load/hourly-load.component';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {
  provideHttpClient,
  withInterceptorsFromDi,
} from '@angular/common/http';
import { DurationMsPipe } from './pipes/duration-ms.pipe';
import { OverviewComponent } from './dashboard/overview/overview.component';
import { DateDifferencePipe } from './pipes/date-difference.pipe';
import { MonitorLevelComponent } from './shared/monitor-level/monitor-level.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { APP_BASE_HREF } from '@angular/common';
import { MenuComponent } from './elements/menu/menu.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ExceptionsComponent } from './endpoint/exceptions/exceptions.component';
import { EndpointDetailsComponent } from './shared/endpoint-details/endpoint-details.component';
import { PaginationComponent } from './shared/pagination/pagination.component';
import { SyntaxHighlightComponent } from './endpoint/exceptions/syntax-highlight/syntax-highlight.component';
import { PlotlyComponent } from './shared/plotly/plotly.component';
import { HourlyApiUtilizationComponent } from './dashboard/hourly-api-utilization/hourly-api-utilization.component';
import { DateShortPipe } from './pipes/date-short.pipe';
import { ExceptionOverviewComponent } from './dashboard/exception-overview/exception-overview.component';
import { DateLayoutPipe } from './pipes/date-layout.pipe';
import { MultiVersionComponent } from './dashboard/multi-version/multi-version.component';
import { DailyApiUtilizationComponent } from './dashboard/daily-api-utilization/daily-api-utilization.component';
import { ApiPerformanceComponent } from './dashboard/api-performance/api-performance.component';
//import { ReportingComponent } from './dashboard/reporting/reporting.component';

@NgModule({
  declarations: [
    AppComponent,
    DurationMsPipe,
    OverviewComponent,
    DateDifferencePipe,
    ExceptionsComponent,
    HourlyLoadComponent,
    HourlyApiUtilizationComponent,
    SyntaxHighlightComponent,
    PlotlyComponent,
    DateShortPipe,
    ExceptionOverviewComponent,
    MultiVersionComponent,
    DailyApiUtilizationComponent,
    ApiPerformanceComponent,
    //ReportingComponent,
  ],
  bootstrap: [AppComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    FontAwesomeModule,
    MenuComponent,
    MonitorLevelComponent,
    EndpointDetailsComponent,
    PaginationComponent,
    NgbModule,
  ],
  providers: [
    DateShortPipe,
    DateLayoutPipe,
    provideHttpClient(withInterceptorsFromDi()),
    { provide: APP_BASE_HREF, useValue: '/dashboard/' },
  ],
})
export class AppModule {}
