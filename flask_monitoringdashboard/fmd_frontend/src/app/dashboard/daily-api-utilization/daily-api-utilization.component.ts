import { Component, EventEmitter, OnInit } from '@angular/core';
import { combineLatest, take, tap } from 'rxjs';
import { MultiSelectionService } from 'src/app/service/multi-select/multi-selection.service';
import { Chart } from 'src/app/service/plotly.service';
import { RequestService } from 'src/app/service/request/request.service';
import { VersionService } from 'src/app/service/version/version.service';
import {
  MultiSelect,
  SelectionFilter,
} from 'src/app/shared/plotly/plotly.component';

@Component({
  selector: 'app-daily-api-utilization',
  templateUrl: './daily-api-utilization.component.html',
  styleUrls: ['./daily-api-utilization.component.css'],
  standalone: false,
})
export class DailyApiUtilizationComponent {
  public title = 'Daily API Utilization';
  public axesText =
    'The X-axis presents the amount of requests. The Y-axis presents a number of days.';
  public contentText =
    'This graph presents a horizontal stacked barplot. Each endpoint is represented ' +
    'by a color. In the legend on the right, you can disable a certain endpoint by clicking on it. You can ' +
    'also show in the information of a single endpoint by double clicking that endpoint in the legend. The ' +
    'information from this graph can be used to see on which days (a subset of) the endpoints are used the most.';

  public graphDataEmitter: EventEmitter<Partial<Chart>> = new EventEmitter();

  public selections: MultiSelect[] = [];

  constructor(private readonly requestService: RequestService) {}

  fetchData(filter: SelectionFilter): void {
    this.requestService
      .getRequests(filter.startDate!, filter.endDate!)
      .pipe(take(1))
      .subscribe((rqs) => {
        this.graphDataEmitter.emit({
          data: rqs.data.map((info) => ({
            x: info.values,
            y: rqs.days,
            name: info.name,
            type: 'bar',
            orientation: 'h',
          })) as any,
          layout_ext: {
            barmode: 'stack',
            xaxis: {
              title: {
                text: 'Number of requests',
              },
            },
            yaxis: {
              type: 'category',
              autorange: 'reversed',
            },
          },
        });
      });
  }
}
