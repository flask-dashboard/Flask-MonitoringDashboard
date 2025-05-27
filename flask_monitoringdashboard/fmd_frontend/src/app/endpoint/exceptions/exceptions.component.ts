import { PaginationDetails } from './../../shared/pagination/pagination.component';
import {
  Component,
  EventEmitter,
  OnDestroy,
  OnInit,
  QueryList,
  ViewChildren,
} from '@angular/core';
import {
  combineLatest,
  filter,
  map,
  mergeMap,
  of,
  Subject,
  takeUntil,
} from 'rxjs';
import { EndpointContextService } from 'src/app/service/endpoint-context/endpoint-context.service';
import { EndpointInfo } from 'src/app/service/endpoint/endpoint-defs';
import { ExceptionDetails } from 'src/app/service/exception/exception-defs';
import { ExceptionService } from 'src/app/service/exception/exception.service';

@Component({
  selector: 'app-exceptions',
  templateUrl: './exceptions.component.html',
  styleUrls: ['./exceptions.component.css'],
  standalone: false,
})
export class ExceptionsComponent implements OnInit, OnDestroy {
  public endpoint: EndpointInfo | null = null;
  public paginationConfig: PaginationDetails = {
    page: 1,
    perPage: 5,
    offset: 0,
    total: 0,
  };
  public table: ExceptionDetails[] = [];
  public paginationEmitter: EventEmitter<PaginationDetails> =
    new EventEmitter();
  private destoyed = new Subject<void>();

  constructor(
    private readonly endpointContext: EndpointContextService,
    private readonly exceptionService: ExceptionService
  ) {}

  ngOnDestroy(): void {
    this.destoyed.next();
    this.destoyed.complete();
  }

  ngOnInit() {
    combineLatest([
      this.endpointContext.endpoint,
      this.paginationEmitter.asObservable(),
    ])
      .pipe(
        takeUntil(this.destoyed),
        filter(([endpoint]) => endpoint !== undefined && endpoint !== null),
        mergeMap(([endpoint]) => {
          this.endpoint = endpoint;
          if (this.paginationConfig.total === 0) {
            return this.exceptionService
              .getNumberOfExceptions(endpoint!.id)
              .pipe(map((numExceptions) => ({ numExceptions, endpoint })));
          }
          return of({ numExceptions: this.paginationConfig.total, endpoint });
        }),
        map(({ numExceptions, endpoint }) => {
          this.paginationConfig.total = numExceptions;
          return endpoint;
        }),
        mergeMap((endpoint) =>
          this.exceptionService.getExceptionDetails(
            endpoint!.id,
            this.paginationConfig.offset,
            this.paginationConfig.perPage
          )
        )
      )
      .subscribe((details) => {
        this.table = details;
      });

    this.onPageChange(this.paginationConfig);
  }

  onPageChange(config: PaginationDetails): void {
    this.paginationEmitter.emit(config);
  }
}
