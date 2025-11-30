import { Component, EventEmitter, OnInit } from '@angular/core';
import { Data } from 'plotly.js';
import { catchError, EMPTY, Observable, take, tap } from 'rxjs';
import { EndpointService } from 'src/app/service/endpoint/endpoint.service';
import { Chart, HeatMap } from 'src/app/service/plotly.service';
import {
  AnswerType,
  IAnswer,
  MedianLatencyAnswer,
  ReportInterval,
  StatusCodeDistributionAnswer,
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
  public title = '';
  public axesText = '';
  public contentText = '';

  public graphDataEmitter: EventEmitter<Partial<Chart>> = new EventEmitter();

  public activeSection: Section = 'custom';
  public reports: Map<Section, Summary[]> = new Map();

  public monthName: string = this.time.fnow('MMMM');
  public previousMonthName: string = this.time.fnow('MMMM', 1, 'month');

  public currentDay: string = this.time.fnow('MMM DD');
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

  public selectedSummary: Summary | undefined;
  public selectedAnswer: MedianLatencyAnswer | undefined;

  public answerType = AnswerType;

  constructor(
    private readonly time: TimeMachineService,
    private readonly versionService: VersionService,
    private readonly reportingService: ReportingService
  ) {}

  ngOnInit() {}

  selectSection(section: Section): void {
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

  selectEntry(summary: Summary, answer: MedianLatencyAnswer): void {
    this.selectedSummary = summary;
    this.selectedAnswer = answer;

    const { comparison, baseline } = this.selectedAnswer.latencies_samples;

    const data: Partial<Data>[] = [
      {
        name: `Comparison (N=${comparison.length})`,
        type: 'violin',
        y: comparison,
      },
      {
        name: `Baseline (N=${baseline.length})`,
        type: 'violin',
        y: baseline,
      },
    ];

    this.graphDataEmitter.emit({
      data: data,
      layout_ext: {
        yaxis: {
          title: {
            text: 'Execution time (ms)',
          },
          rangemode: 'nonnegative',
        },
      },
    });
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

  castToMedianAnswer(answer: IAnswer): MedianLatencyAnswer {
    return answer as MedianLatencyAnswer;
  }

  castToStatusDistributionAnswer(
    answer: IAnswer
  ): StatusCodeDistributionAnswer {
    return answer as StatusCodeDistributionAnswer;
  }
}
