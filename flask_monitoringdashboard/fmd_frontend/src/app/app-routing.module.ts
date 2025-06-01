import { Component, NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OverviewComponent } from './dashboard/overview/overview.component';
import { HourlyApiUtilizationComponent } from './dashboard/hourly-api-utilization/hourly-api-utilization.component';
import { ExceptionsComponent } from './endpoint/exceptions/exceptions.component';
import { HourlyLoadComponent } from './endpoint/hourly-load/hourly-load.component';
import { ExceptionOverviewComponent } from './dashboard/exception-overview/exception-overview.component';
import { MultiVersionComponent } from './dashboard/multi-version/multi-version.component';
import { DailyApiUtilizationComponent } from './dashboard/daily-api-utilization/daily-api-utilization.component';
import { ApiPerformanceComponent } from './dashboard/api-performance/api-performance.component';
@Component({ template: '<p>Dashboard Parent Hit</p>' })
export class TempDashboardParentComponent {}

const routes: Routes = [
  { path: 'overview', component: OverviewComponent },
  { path: 'hourly_load', component: HourlyApiUtilizationComponent },
  { path: 'exception_overview', component: ExceptionOverviewComponent },
  { path: 'multi_version', component: MultiVersionComponent },
  { path: 'daily_utilization', component: DailyApiUtilizationComponent },
  { path: 'api_performance', component: ApiPerformanceComponent },
  //{ path: 'reporting', component: ReportingComponent },
  {
    path: 'endpoint/:id',
    children: [
      { path: 'exceptions', component: ExceptionsComponent },
      { path: 'hourly_load', component: HourlyLoadComponent },
    ],
  },

  {
    path: '',
    redirectTo: 'overview',
    pathMatch: 'full',
  },
  //{ path: 'dasboard', redirectTo: 'dasboard/overview', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
