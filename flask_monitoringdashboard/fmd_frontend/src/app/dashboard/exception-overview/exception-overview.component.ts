import { ExceptionService } from './../../service/exception/exception.service';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import {
  map,
  mergeMap,
  of,
  Subject,
  switchMap,
  take,
  takeUntil,
  tap,
} from 'rxjs';
import { ExceptionGroup } from 'src/app/service/exception/exception-defs';
import { PaginationDetails } from 'src/app/shared/pagination/pagination.component';

@Component({
  selector: 'app-exception-overview',
  templateUrl: './exception-overview.component.html',
  styleUrls: ['./exception-overview.component.css'],
  standalone: false,
})
export class ExceptionOverviewComponent implements OnInit, OnDestroy {
  public table: ExceptionGroup[] = [];
  public paginationConfig: PaginationDetails = {
    page: 1,
    perPage: 5,
    offset: 0,
  };
  public total: number | undefined;

  private paginationEmitter: EventEmitter<PaginationDetails> =
    new EventEmitter();
  private _destroyed: Subject<void> = new Subject();

  constructor(private readonly exceptionService: ExceptionService) {}

  ngOnDestroy(): void {
    this._destroyed.next();
    this._destroyed.complete();
    this.paginationEmitter.complete();
  }

  ngOnInit() {
    this.paginationEmitter
      .asObservable()
      .pipe(
        takeUntil(this._destroyed),
        mergeMap((pagination) => {
          if (this.total === undefined) {
            return this.exceptionService.getNumberOfExceptions().pipe(
              tap((exceptions) => (this.total = exceptions)),
              map(() => pagination)
            );
          }
          return of(pagination);
        }),
        mergeMap((pagination) =>
          this.exceptionService.getExceptionGroups(
            pagination.offset,
            pagination.perPage
          )
        )
      )
      .subscribe((groups) => (this.table = groups));
    this.onPageChange(this.paginationConfig);
  }

  onPageChange(config: PaginationDetails): void {
    this.paginationEmitter.emit(config);
  }
}
