import { Component, EventEmitter, inject, OnInit } from '@angular/core';
import { forkJoin, map, switchMap, take } from 'rxjs';
import { DateLayoutPipe } from 'src/app/pipes/date-layout.pipe';
import { EndpointContextService } from 'src/app/service/endpoint-context/endpoint-context.service';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { HeatMap } from 'src/app/service/plotly.service';
import { MultiSelect, SelectionFilter } from 'src/app/shared/plotly/plotly.component';
import { EndpointService } from 'src/app/service/endpoint/endpoint.service';
import { MultiSelectionService } from 'src/app/service/multi-select/multi-selection.service';

@Component({
  selector: 'app-endpoint-version-ip',
  templateUrl: './version-ip.component.html',
  styleUrls: ['./version-ip.component.css'],
  standalone: false,
})
export class EndpointVersionIpComponent implements OnInit {
  private readonly endpointContext = inject(EndpointContextService);
  private readonly endpointService = inject(EndpointService);
  private readonly multiSelection = inject(MultiSelectionService);
  private readonly dateLayoutPipe = inject(DateLayoutPipe);

  protected endpoint?: EndpointInfo;
  protected readonly eventEmitter = new EventEmitter<Partial<HeatMap>>();
  protected title?: string;
  protected selectData: MultiSelect[] = [];

  protected axesText = 'In this graph, the X-axis presents the versions that are used. The Y-axis presents ' +
    '(a subset of) all IP-addresses. You can use the slider to select a subset of all IP-addresses.';
  protected contentText = 'The cell color represents the average response time (expressed in ms) of this ' +
    'endpoint per IP per version.';

  ngOnInit() {
    this.endpointContext.endpoint.pipe(
      take(1),
      switchMap(endpoint => {
        this.title = `IP-Focused Multi-Version Performance for ${endpoint.endpoint}`;
        this.endpoint = endpoint;
        return forkJoin([
          this.multiSelection.getVersions(),
          this.multiSelection.getIPAddresses(),
        ]);
      })
    ).subscribe(([versions, ips]) => {
      this.selectData = [versions, ips];
    });
  }

  fetchData(selectionFilter: SelectionFilter): void {
    if (!this.endpoint) return;

    const versions = selectionFilter.selected.find(s => s.name === 'versions')?.selected.map(v => v.id) ?? [];
    const ips = selectionFilter.selected.find(s => s.name === 'IP-addresses')?.selected.map(ip => ip.id) ?? [];

    this.endpointService.getVersionIp(this.endpoint.id, versions, ips)
      .pipe(
        take(1),
        map(data => ({
          x: data.versions.map(obj => obj.version + '<br>' + this.dateLayoutPipe.transform(obj.date)),
          y: ips,
          z: data.data,
        }))
      )
      .subscribe(({ x, y, z }) => {
        this.eventEmitter.emit({
          x,
          y,
          z,
          layout_ext: {
            xaxis: { type: 'category', title: { text: 'Versions' } },
            yaxis: { type: 'category', title: { text: 'IP-addresses' } },
          }
        });
      });
  }
}
