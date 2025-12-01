import { Component, EventEmitter, inject, input, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Data } from 'plotly.js';
import { Chart } from 'src/app/service/plotly.service';
import {
  MedianLatencyAnswer,
  Summary,
} from 'src/app/service/reporting/reporting-defs';

export interface ReportModalData {
  selectedSummary: Summary;
  selectedAnswer: MedianLatencyAnswer;
  data: Partial<Data>[];
}

@Component({
  selector: 'app-report-modal',
  templateUrl: './report-modal.component.html',
  styleUrls: [],
  standalone: false,
})
export class ReportModal {
  readonly dialogRef = inject(MatDialogRef<ReportModal>);
  readonly data = inject<ReportModalData>(MAT_DIALOG_DATA);
  public graphData: Partial<Chart> = {
    data: this.data.data,
    layout_ext: {
      yaxis: {
        title: {
          text: 'Execution time (ms)',
        },
        rangemode: 'nonnegative',
      },
    },
  };
  readonly selectedSummary = this.data.selectedSummary;
  readonly selectedAnswer = this.data.selectedAnswer;
  public title = '';
  public axesText = '';
  public contentText = '';


  close(): void {
    this.dialogRef.close();
  }
}
