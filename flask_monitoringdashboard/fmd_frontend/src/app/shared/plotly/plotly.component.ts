import { Subject, takeUntil } from 'rxjs';
import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { FormArray, FormControl, FormGroup } from '@angular/forms';
import { Chart, HeatMap, PlotlyService } from 'src/app/service/plotly.service';

export interface MultiSelectValue {
  id: string;
  text: string;
}

export interface MultiSelect {
  name: string;
  values: MultiSelectValue[];
  selected: MultiSelectValue[];
}

export interface SelectionFilter {
  startDate: Date | null;
  endDate: Date | null;
  selected: MultiSelect[];
}

@Component({
  selector: 'app-plotly',
  templateUrl: './plotly.component.html',
  styleUrls: ['./plotly.component.css'],
  standalone: false,
})
export class PlotlyComponent implements OnInit, OnDestroy {
  @Input() public useDateRange: boolean = false;
  @Input() public useMultiSelect: boolean = false;
  @Input() public selectData: MultiSelect[] = [];
  @Input() public title!: string;
  @Input() public graphText: string =
    'You can hover the graph with your mouse to see the actual values. You can also use the ' +
    'buttons at the top of the graph to select a subset of graph, scale it accordingly, or save the graph ' +
    'as a PNG image.';
  @Input() public axesText!: string;
  @Input() public contentText!: string;
  @Input() public graphType!: 'heatmap' | 'chart';
  @Input() public graphDataEmitter!: EventEmitter<
    Partial<HeatMap> | Partial<Chart>
  >;

  @Output() public formChange: EventEmitter<SelectionFilter> =
    new EventEmitter();

  private _destroyed: Subject<void> = new Subject();

  public filterForm: FormGroup = new FormGroup({
    startDate: new FormControl<Date | null>(null),
    endDate: new FormControl<Date | null>(null),
    multiSelect: new FormArray<
      FormGroup<{
        name: FormControl<string>;
        values: FormControl<MultiSelectValue[]>;
        selected: FormControl<MultiSelectValue[]>;
      }>
    >([]),
  });

  public isLoading = true;

  @ViewChild('chart') chartElm!: ElementRef;

  constructor(private readonly plotly: PlotlyService) {}

  ngOnDestroy(): void {
    this._destroyed.next();
    this._destroyed.complete();
    this.formChange.complete();
  }

  ngOnInit() {
    if (this.useDateRange) {
      const startDate = new Date();
      const endDate = new Date();
      startDate.setDate(endDate.getDate() - 14);
      this.filterForm.get('startDate')?.setValue(startDate);
      this.filterForm.get('endDate')?.setValue(endDate);
    }

    if (this.useMultiSelect) {
      const msFormArray = this.filterForm.get('multiSelect') as FormArray<
        FormGroup<{
          name: FormControl<string>;
          values: FormControl<MultiSelectValue[]>;
          selected: FormControl<MultiSelectValue[]>;
        }>
      >;

      this.selectData.forEach((data) => {
        msFormArray.push(
          new FormGroup({
            name: new FormControl<string>(data.name, { nonNullable: true }),
            values: new FormControl<MultiSelectValue[]>(data.values, {
              nonNullable: true,
            }),
            selected: new FormControl<MultiSelectValue[]>(data.selected, {
              nonNullable: true,
            }),
          })
        );
      });
    }

    this.formChange.emit(this.formAsSelectionFilter());
    this.filterForm.valueChanges
      .pipe(takeUntil(this._destroyed))
      .subscribe((_) => this.formChange.emit(this.formAsSelectionFilter()));
    this.graphDataEmitter
      .asObservable()
      .pipe(takeUntil(this._destroyed))
      .subscribe((data) => {
        const res = { root: this.chartElm.nativeElement, ...data };
        switch (this.graphType) {
          case 'heatmap':
            this.plotly.heatmap(res as HeatMap);
            break;
          case 'chart':
            this.plotly.chart(res as Chart);
            break;
        }
        this.isLoading = false;
      });
  }

  formAsSelectionFilter(): SelectionFilter {
    return {
      startDate: this.filterForm.get('startDate')?.value,
      endDate: this.filterForm.get('endDate')?.value,
      selected: this.filterForm.get('multiSelect')?.value as MultiSelect[],
    };
  }

  getMultiSelect(): MultiSelect[] {
    const ms = this.filterForm.get('multiSelect') as FormArray<
      FormControl<MultiSelect>
    >;
    return ms.controls.map((control) => control.value);
  }

  getMultiSelectFormArray(): FormArray<
    FormGroup<{
      name: FormControl<string>;
      values: FormControl<MultiSelectValue[]>;
      selected: FormControl<MultiSelectValue[]>;
    }>
  > {
    return this.filterForm.get('multiSelect') as FormArray<
      FormGroup<{
        name: FormControl<string>;
        values: FormControl<MultiSelectValue[]>;
        selected: FormControl<MultiSelectValue[]>;
      }>
    >;
  }
}
