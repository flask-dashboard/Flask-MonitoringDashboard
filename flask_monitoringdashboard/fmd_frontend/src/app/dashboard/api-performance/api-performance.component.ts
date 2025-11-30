import { Component, EventEmitter, OnInit } from '@angular/core';
import { combineLatest, take, takeUntil, tap } from 'rxjs';
import { EndpointService } from 'src/app/service/endpoint/endpoint.service';
import { MultiSelectionService } from 'src/app/service/multi-select/multi-selection.service';
import { Chart, HeatMap } from 'src/app/service/plotly.service';
import { VersionService } from 'src/app/service/version/version.service';
import {
  MultiSelect,
  SelectionFilter,
} from 'src/app/shared/plotly/plotly.component';

@Component({
  selector: 'app-api-performance',
  templateUrl: './api-performance.component.html',
  styleUrls: ['./api-performance.component.css'],
  standalone: false,
})
export class ApiPerformanceComponent implements OnInit {
  public title = 'API Performance';
  public axesText =
    'The X-axis presents the versions that are used. The Y-axis presents the' +
    'endpoints that are found in the Flask application.';
  public contentText =
    'The color of the cell presents the distribution of the amount of requests ' +
    'that the application received in a single version for a single endpoint. The darker the cell, ' +
    'the more requests a certain endpoint has processed in that version. Since it displays the ' +
    'distribution of the load, each column sums up to 100%. This information can be used to discover ' +
    'which endpoints process the most requests.';

  public graphDataEmitter: EventEmitter<Partial<Chart>> = new EventEmitter();

  public selections: MultiSelect[] = [];

  constructor(
    private readonly msService: MultiSelectionService,
    private readonly endpointService: EndpointService
  ) { }

  ngOnInit(): void {
    this.msService
      .getEndpoints()
      .pipe(
        take(1),
        tap((endpoints) => this.selections.push(endpoints)),
      )
      .subscribe();
  }

  fetchData(filter: SelectionFilter): void {
    const [endpoints] = filter.selected;
    this.endpointService
      .getApiPerformance(endpoints)
      .pipe(take(1))
      .subscribe((perfs) => {
        this.graphDataEmitter.emit({
          data: perfs.map((perf) => ({
            x: perf.values,
            type: 'box',
            name: perf.name,
          })),
          layout_ext: {
            xaxis: {
              title: {
                text: 'Execution time (ms)',
              },
            },
            yaxis: {
              type: 'category',
            },
          },
        });
      });
  }
}
