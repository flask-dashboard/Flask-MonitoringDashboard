import { NgFor } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { take } from 'rxjs';
import { DashboardService } from 'src/app/service/dashboard/dashboard.service';

@Component({
  selector: 'app-monitor-level',
  templateUrl: './monitor-level.component.html',
  styleUrls: ['./monitor-level.component.css'],
  standalone: true,
  imports: [NgFor],
})
export class MonitorLevelComponent implements OnInit {
  @Input() public monitoringLevel!: number;
  @Input() public endpointName!: string;
  constructor(private readonly endpointService: DashboardService) {}

  ngOnInit() {}

  sendForm(val: number): void {
    this.monitoringLevel = val;
    this.endpointService
      .setRule(this.endpointName, this.monitoringLevel)
      .pipe(take(1))
      .subscribe();
  }

  computeColor(level: number): string {
    let a = 0.2;
    if (this.monitoringLevel === level) {
      a = 1;
    }

    let red = [230, 74, 54];
    let green = [237, 255, 77];

    // level 0 = total green, level 3 = total red
    let percentage = level / 3.0;
    let r = red[0] * percentage + green[0] * (1 - percentage);
    let g = red[1] * percentage + green[1] * (1 - percentage);
    let b = red[2] * percentage + green[2] * (1 - percentage);

    return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + a + ')';
  }
}
