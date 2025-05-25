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
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { APP_BASE_HREF } from '@angular/common';
import { MenuComponent } from './elements/menu/menu.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ExceptionsComponent } from './endpoint/exceptions/exceptions.component';

@NgModule({
  declarations: [
    AppComponent,
    DurationMsPipe,
    OverviewComponent,
    DateDifferencePipe,
    MonitorLevelComponent,
    ExceptionsComponent,
    HourlyLoadComponent,
  ],
  bootstrap: [AppComponent],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    FontAwesomeModule,
    MenuComponent,
    NgbModule,
  ],
  providers: [
    provideHttpClient(withInterceptorsFromDi()),
    { provide: APP_BASE_HREF, useValue: '/dashboard/' },
  ],
})
export class AppModule {}
