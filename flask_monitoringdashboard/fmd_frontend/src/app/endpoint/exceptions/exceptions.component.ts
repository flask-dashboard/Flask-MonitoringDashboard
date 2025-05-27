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
  switchMap,
  takeUntil,
  tap,
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
  };
  public table: ExceptionDetails[] = [];
  public paginationEmitter: EventEmitter<PaginationDetails> =
    new EventEmitter();
  private destoyed = new Subject<void>();
  public total: number | undefined;

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
        mergeMap(([endpoint, _]) => {
          if (this.total === undefined) {
            return this.exceptionService.getNumberOfExceptions().pipe(
              tap((exceptions) => (this.total = exceptions)),
              map(() => endpoint)
            );
          }
          return of(endpoint);
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
