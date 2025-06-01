import { Component, OnInit } from '@angular/core';
import { catchError, EMPTY, Observable, take, tap } from 'rxjs';
import { EndpointService } from 'src/app/service/endpoint/endpoint.service';
import {
  ReportInterval,
  Summary,
} from 'src/app/service/reporting/reporting-defs';
import { ReportingService } from 'src/app/service/reporting/reporting.service';
import { TimeMachineService } from 'src/app/service/time-machine.service';
import { EndpointVersion } from 'src/app/service/version/version-defs';
import { VersionService } from 'src/app/service/version/version.service';

type Section = 'custom' | 'commits' | 'month' | 'week' | 'day';

@Component({
  selector: 'app-reporting',
  templateUrl: './reporting.component.html',
  styleUrls: ['./reporting.component.css'],
  standalone: false,
})
export class ReportingComponent implements OnInit {
  public activeSection: Section = 'custom';
  public reports: Map<Section, Summary[]> = new Map();

  public monthName: string = this.time.fnow('MMMM');
  public previousMonthName: string = this.time.fnow('MMMM', 1, 'month');

  public currentDaty: string = this.time.fnow('MMM DD');
  public yesterday: string = this.time.fnow('MMM DD', 1, 'days');

  public currentWeekNumber: number = this.time.now().isoWeek();
  public previousWeekNumber: number = this.time
    .now()
    .subtract(1, 'weeks')
    .isoWeek();

  public generating: boolean = false;
  public onlyShowInteresting: boolean = false;

  public intervals: ReportInterval = this.time.intervals(1, 'months');

  public versions: EndpointVersion[] = [];

  public commitVersion: string | null = null;
  public baselineCommitVersion: string | null = null;

  public error: string | undefined;

  constructor(
    private readonly time: TimeMachineService,
    private readonly versionService: VersionService,
    private readonly reportingService: ReportingService
  ) {}

  ngOnInit() {}

  selectSetion(section: Section): void {
    this.activeSection = section;
    if (section == 'commits' && this.versions.length === 0) {
      this.versionService
        .getVersions()
        .pipe(take(1))
        .subscribe((versions) => (this.versions = versions));
      return;
    } else if (section === 'commits') {
      return;
    }

    const INTERVAL_SIZES = {
      day: [1, 'days'],
      week: [1, 'isoWeeks'],
      month: [1, 'months'],
      custom: [1, 'isoWeeks'],
    };

    const [amnt, type] = INTERVAL_SIZES[section];
    this.intervals = this.time.intervals(amnt, type as any);
  }

  generateReport(): void {
    this.generating = true;
    this.error = undefined;

    let summary: Observable<Summary[]>;
    if (
      this.activeSection === 'commits' &&
      this.commitVersion &&
      this.baselineCommitVersion
    ) {
      summary = this.reportingService.createReportFromCommits(
        this.commitVersion,
        this.baselineCommitVersion
      );
    } else {
      summary = this.reportingService.createReportFromIntervals(
        this.intervals.comparison,
        this.intervals.baseline,
        true
      );
    }

    summary
      .pipe(
        take(1),
        tap((res) => this.reports.set(this.activeSection, res)),
        catchError((err) => {
          this.error = err;
          return EMPTY;
        }),
        tap((_) => (this.generating = false))
      )
      .subscribe();
  }
}
