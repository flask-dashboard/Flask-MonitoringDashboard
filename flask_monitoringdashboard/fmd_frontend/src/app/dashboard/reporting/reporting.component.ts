import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  inject,
} from '@angular/core';
import { Data } from 'plotly.js';
import { catchError, EMPTY, Observable, take, tap } from 'rxjs';
import { Chart } from 'src/app/service/plotly.service';
import {
  AnswerType,
  IAnswer,
  MedianLatencyAnswer,
  ReportInterval,
  StatusCodeDistributionAnswer,
  Summary,
  SummaryWrapper,
} from 'src/app/service/reporting/reporting-defs';
import { ReportingService } from 'src/app/service/reporting/reporting.service';
import { TimeMachineService } from 'src/app/service/time-machine.service';
import { EndpointVersion } from 'src/app/service/version/version-defs';
import { VersionService } from 'src/app/service/version/version.service';
import { MatDialog } from '@angular/material/dialog';
import {
  ReportModal,
  ReportModalData,
} from './report-modal/report-modal.component';

type Section = 'custom' | 'commits' | 'month' | 'week' | 'day';

@Component({
  selector: 'app-reporting',
  templateUrl: './reporting.component.html',
  styleUrls: ['./reporting.component.css'],
  standalone: false,
})
export class ReportingComponent {
  private readonly time = inject(TimeMachineService);
  private readonly versionService = inject(VersionService);
  private readonly reportingService = inject(ReportingService);
  private readonly dialog = inject(MatDialog);


  public activeSection: Section = 'custom';
  public reports: Map<Section, SummaryWrapper> = new Map();

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

  public answerType = AnswerType;

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

    const { comparison, baseline } = answer.latencies_samples;

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


    this.dialog.open<ReportModal, ReportModalData>(ReportModal, {
      disableClose: false,
      data: {
        selectedSummary: summary,
        selectedAnswer: answer,
        data: data,
      },
      height: '75%',
      width: '75%'
    });
  }

  generateReport(): void {
    this.generating = true;
    this.error = undefined;

    let summary: Observable<SummaryWrapper>;
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
        tap(
          (res) =>
            (this.reports = new Map(this.reports.set(this.activeSection, res)))
        ),
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
