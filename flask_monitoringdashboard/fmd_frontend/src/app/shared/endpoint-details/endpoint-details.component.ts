import { Component, OnInit } from '@angular/core';
import { EndpointContextService } from 'src/app/service/endpoint-context/endpoint-context.service';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { MonitorLevelComponent } from '../monitor-level/monitor-level.component';
import { take, Observable } from 'rxjs';
import { AsyncPipe, NgIf } from '@angular/common';

@Component({
  selector: 'app-endpoint-details',
  templateUrl: './endpoint-details.component.html',
  styleUrls: ['./endpoint-details.component.css'],
  imports: [MonitorLevelComponent, NgIf, AsyncPipe],
})
export class EndpointDetailsComponent implements OnInit {
  public endpoint$!: Observable<EndpointInfo | null>;

  constructor(private readonly endpointContext: EndpointContextService) {}

  ngOnInit() {
    this.endpoint$ = this.endpointContext.endpoint;
  }
}
