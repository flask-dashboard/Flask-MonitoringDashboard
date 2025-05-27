import { Component, OnInit, EventEmitter } from '@angular/core';
import { take } from 'rxjs';
import { DateShortPipe } from 'src/app/pipes/date-short.pipe';
import { HeatMap } from 'src/app/service/plotly.service';
import { RequestService } from 'src/app/service/request/request.service';
import { SelectionFilter } from 'src/app/shared/plotly/plotly.component';

@Component({
  selector: 'app-hourly-api-utilization',
  templateUrl: './hourly-api-utilization.component.html',
  styleUrls: ['./hourly-api-utilization.component.css'],
  standalone: false,
})
export class HourlyApiUtilizationComponent implements OnInit {
  public title = 'Hourly API Utilization';
  public axesText =
    'The X-axis represents the dates. The Y-axis presents the hours of the day.';
  public contentText =
    'The cell color represents the number of requests that the application ' +
    'received in a single hour. The darker the cell, the more requests it has processed. This information ' +
    'can be used to to discover the peak usage hours of the Flask application.';

  public graphDataEmitter: EventEmitter<Partial<HeatMap>> = new EventEmitter();

  constructor(
    private readonly requestService: RequestService,
    private readonly dateShortPipe: DateShortPipe
  ) {}

  ngOnInit() {}

  fetchData(filter: SelectionFilter): void {
    this.requestService
      .getHourlyLoad(filter.startDate!, filter.endDate!)
      .pipe(take(1))
      .subscribe((data) => {
        const x = data.days;
        const y = [...Array(24).keys()].map((d) => d + ':00');
        const z = data.data;
        this.graphDataEmitter.emit({
          x,
          y,
          z,
          hover_text: data.data.map((row, i) =>
            row.map((item, j) => {
              return `Date: ${this.dateShortPipe.transform(x[j])}<br>Time: ${
                i + ':00'
              }<br>Requests: ${item}`;
            })
          ),
          layout_ext: {
            yaxis: { autorange: 'reversed' },
            margin: { l: 50 },
          },
        });
      });
  }
}
