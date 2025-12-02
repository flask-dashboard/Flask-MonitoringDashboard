import { VersionService } from './../../service/version/version.service';
import { AfterViewInit, Component, EventEmitter, inject, OnInit } from '@angular/core';
import { combineLatest, filter, merge, take, tap } from 'rxjs';
import { DateLayoutPipe } from 'src/app/pipes/date-layout.pipe';
import { EndpointContextService } from 'src/app/service/endpoint-context/endpoint-context.service';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { MultiSelectionService } from 'src/app/service/multi-select/multi-selection.service';
import { HeatMap } from 'src/app/service/plotly.service';
import {
  MultiSelect,
  SelectionFilter,
} from 'src/app/shared/plotly/plotly.component';

@Component({
  selector: 'app-user-multi-version',
  templateUrl: './user-multi-version.component.html',
  styleUrls: ['./user-multi-version.component.css'],
  standalone: false,
})
export class UserMultiVersionComponent implements AfterViewInit {
  private readonly msService = inject(MultiSelectionService);
  private readonly versionService = inject(VersionService);
  private readonly endpointContext = inject(EndpointContextService);
  private readonly dateLayout = inject(DateLayoutPipe)
  protected endpoint?: EndpointInfo
  public title = 'Multi version API Utilization';
  public axesText =
    'In this graph, the X-axis presents the versions that are used. The Y-axis ' +
    'presents (a subset of) all unique users, as specified by "dashboard.config.group_by". You can ' +
    'use the slider to select a subset of the all unique users.';
  public contentText =
    'The cell color represents the average response time (expressed in ms) of this endpoint ' +
    'per user per version.';
  public graphDataEmitter: EventEmitter<Partial<HeatMap>> = new EventEmitter();

  public selections?: MultiSelect[];

  ngAfterViewInit(): void {
    combineLatest([this.msService.getVersions(), this.msService.getUsers()])
      .pipe(
        take(1),
        tap(([versions, users]) =>
          (this.selections = [versions, users])
        )
      )
      .subscribe();

    this.endpointContext.endpoint.pipe(
      tap(endpoint => (this.endpoint = endpoint))
    ).subscribe();
  }

  fetchData(filter: SelectionFilter): void {
    const [versions, users] = filter.selected;
    if (this.endpoint) {

      this.versionService
        .getVersionUserUtilization(users, versions, this.endpoint.id)
        .pipe(take(1))
        .subscribe((response) => {
          this.graphDataEmitter.emit({
            x: response.versions.map(
              obj => obj.version + '<br>' + this.dateLayout.transform(obj.date)
            ),
            y: users.selected.map((sel) => sel.id),
            z: response.data,
            layout_ext: {
              xaxis: {
                type: 'category',
                title: {
                  text: 'Versions'
                }
              },
              yaxis: {
                type: 'category',
                title: { text: 'Users' },
                autorange: 'reversed'
              }
            },
          });
        });
    }
  }
}
