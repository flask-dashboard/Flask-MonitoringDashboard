import { Component, EventEmitter, inject, OnInit } from '@angular/core';
import { filter, take, tap } from 'rxjs';
import { DateShortPipe } from 'src/app/pipes/date-short.pipe';
import { EndpointContextService } from 'src/app/service/endpoint-context/endpoint-context.service';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { HeatMap } from 'src/app/service/plotly.service';
import { RequestService } from 'src/app/service/request/request.service';
import { SelectionFilter } from 'src/app/shared/plotly/plotly.component';

@Component({
  selector: 'app-hourly-load',
  templateUrl: './hourly-load.component.html',
  styleUrls: ['./hourly-load.component.css'],
  standalone: false,
})
export class HourlyLoadComponent implements OnInit {
  private readonly endpointContext = inject(EndpointContextService);
  private readonly requestService = inject(RequestService);
  private readonly dateShortPipe = inject(DateShortPipe);
  protected endpoint?: EndpointInfo;
  protected readonly eventEmitter = new EventEmitter<Partial<HeatMap>>();
  protected title!: string;
  protected axesText = 'The X-axis represents the dates. The Y-axis presents the hours of the day.';
  protected contentText = 'The cell color represents the number of requests that the application ' +
    'received in a single hour for this endpoint. The darker the cell, the more requests it has processed.' +
    ' This information can be used to discover the peak usage hours of this endpoint.';


  ngOnInit() {
    this.endpointContext.endpoint.pipe(
      filter(endpoint => endpoint !== null && endpoint !== undefined),
      tap(endpoint => {
        this.title = `Hourly API Utilization for ${endpoint.endpoint}`;
        this.endpoint = endpoint;
      })
    ).subscribe();
  }

  fetchData(filter: SelectionFilter): void {
    if (this.endpoint) {
      this.requestService
        .getHourlyLoad(filter.startDate!, filter.endDate!, this.endpoint.id)
        .pipe(take(1))
        .subscribe((data) => {
          const x = data.days;
          const y = [...Array(24).keys()].map((d) => d + ':00');
          const z = data.data;
          this.eventEmitter.emit({
            x,
            y,
            z,
            hover_text: data.data.map((row, i) =>
              row.map((item, j) => {
                return `Date: ${this.dateShortPipe.transform(x[j])}<br>Time: ${i + ':00'
                  }<br>Requests: ${item}`;
              })
            ),
            layout_ext: {
              xaxis: {
                type: 'category',
                title: {
                  text: 'Versions'
                }
              },
              yaxis: {
                type: 'category',
                autorange: 'reversed'
              },
              margin: { l: 50 }
            }
          });
        });
    }
  }
}
