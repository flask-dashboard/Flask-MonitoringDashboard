import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { DurationMsPipe } from './pipes/duration-ms.pipe';
import { OverviewComponent } from './dashboard/overview/overview.component';
import { DateDifferencePipe } from './pipes/date-difference.pipe';
import { MonitorLevelComponent } from './shared/monitor-level/monitor-level.component';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@NgModule({ declarations: [
        AppComponent,
        DurationMsPipe,
        OverviewComponent,
        DateDifferencePipe,
        MonitorLevelComponent,
    ],
    bootstrap: [AppComponent], imports: [BrowserModule,
        AppRoutingModule,
        FormsModule,
        FontAwesomeModule], providers: [provideHttpClient(withInterceptorsFromDi())] })
export class AppModule {}
