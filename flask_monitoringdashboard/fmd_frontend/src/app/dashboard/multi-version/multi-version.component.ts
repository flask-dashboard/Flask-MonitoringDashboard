import { VersionService } from './../../service/version/version.service';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { combineLatest, merge, take, tap } from 'rxjs';
import { MultiSelectionService } from 'src/app/service/multi-select/multi-selection.service';
import { HeatMap } from 'src/app/service/plotly.service';
import {
  MultiSelect,
  SelectionFilter,
} from 'src/app/shared/plotly/plotly.component';

@Component({
  selector: 'app-multi-version',
  templateUrl: './multi-version.component.html',
  styleUrls: ['./multi-version.component.css'],
  standalone: false,
})
export class MultiVersionComponent implements OnInit {
  public title = 'Multi version API Utilization';
  public axesText =
    'The X-axis presents the versions that are used. The Y-axis presents the' +
    'endpoints that are found in the Flask application.';
  public contentText =
    'The color of the cell presents the distribution of the amount of requests ' +
    'that the application received in a single version for a single endpoint. The darker the cell, ' +
    'the more requests a certain endpoint has processed in that version. Since it displays the ' +
    'distribution of the load, each column sums up to 100%. This information can be used to discover ' +
    'which endpoints process the most requests.';

  public graphDataEmitter: EventEmitter<Partial<HeatMap>> = new EventEmitter();

  public selections: MultiSelect[] = [];

  constructor(
    private readonly msService: MultiSelectionService,
    private readonly versionService: VersionService
  ) {}

  ngOnInit(): void {
    combineLatest([this.msService.getVersions(), this.msService.getEndpoints()])
      .pipe(
        take(1),
        tap(([versions, endpoints]) =>
          this.selections.push(versions, endpoints)
        )
      )
      .subscribe();
  }

  fetchData(filter: SelectionFilter): void {
    const [versions, endpoints] = filter.selected;
    this.versionService
      .getMultiVersionUtilization(endpoints, versions)
      .pipe(take(1))
      .subscribe((util) => {
        this.graphDataEmitter.emit({
          x: versions.selected.map((sel) => sel.id),
          y: endpoints.selected.map((sel) => sel.id),
          z: util.map((nums) => nums.map((num) => (num == 0 ? NaN : num))),
          layout_ext: {
            xaxis: {
              type: 'category',
              title: { text: 'Versions' },
            },
            yaxis: {
              type: 'category',
            },
          },
        });
      });
  }
}
