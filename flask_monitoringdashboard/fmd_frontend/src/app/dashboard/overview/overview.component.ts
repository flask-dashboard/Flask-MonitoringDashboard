import { Component, OnInit } from '@angular/core';
import { OverviewDto } from 'src/app/service/dashboard/dashboard-defs';
import { DashboardService } from 'src/app/service/dashboard/dashboard.service';
import { from, map, mergeMap, take, tap } from 'rxjs';
import { Router } from '@angular/router';

@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css'],
})
export class OverviewComponent implements OnInit {
  public table: OverviewDto[] = [];
  public blueprints: string[] = [];
  public selectedBlueprint: string = '';
  public isHits: boolean = true;
  public pageSize: number = 10;
  public searchQuery: string = '';
  public sortBy: keyof OverviewDto = 'name';
  public isDesc: boolean = true;
  public currentPage: number = 0;
  public pypi_version: string = '0.0.0';
  public dashboard_version: string = '0.0.0';
  constructor(
    private readonly endpointService: DashboardService,
    private readonly router: Router
  ) {}

  ngOnInit() {
    this.endpointService
      .getOverviewData()
      .pipe(
        take(1),
        tap((data) => {
          this.table = data;
        }),
        mergeMap((item) => from(item)),
        map((item) => item.blueprint),
        tap((blueprint) => {
          if (!this.blueprints.includes(blueprint)) {
            this.blueprints.push(blueprint);
            this.blueprints = [...this.blueprints];
          }
        })
      )
      .subscribe();
  }

  toggleHits(): void {
    this.isHits = !this.isHits;
  }

  changeSortingOrder(column: keyof OverviewDto): void {
    if (column !== this.sortBy) {
      this.isDesc = true;
      this.sortBy = column;
      return;
    }
    this.isDesc = !this.isDesc;
  }

  getSortArrowClassName(column: string): any {
    return {
      'rotate-up': !this.isDesc && this.sortBy === column,
      'rotate-down': this.isDesc && this.sortBy === column,
      'text-gray': this.sortBy !== column,
    };
  }

  ascendingOrder(a: OverviewDto, b: OverviewDto): number {
    console.log(a);
    console.log(b);
    if (!a && !b) return 0;

    const valA = a[this.sortBy];
    const valB = b[this.sortBy];

    if (!valA && valB) return 1;
    if (valA && !valB) return -1;
    if (!valA && !valB) return 0;

    if (this.sortBy === 'last-accessed') {
      const dateA = Date.parse(valA as string);
      const dateB = Date.parse(valB as string);

      if (dateA < dateB) return -1;
      if (dateA > dateB) return 1;
      return 0;
    }

    if (typeof valA === 'string' && typeof valB === 'string') {
      return valA.localeCompare(valB);
    }

    if (typeof valA === 'number' && typeof valB === 'number') {
      return valA - valB;
    }

    if (valA < valB) return -1;
    if (valA > valB) return 1;
    return 0;
  }

  descendingOrder(a: OverviewDto, b: OverviewDto) {
    return this.ascendingOrder(b, a);
  }

  sortItems(items: OverviewDto[]): OverviewDto[] {
    return this.isDesc
      ? items.sort(this.descendingOrder.bind(this))
      : items.sort(this.ascendingOrder.bind(this));
  }

  getItemsForPage(pageNumber: number): OverviewDto[] {
    const start = pageNumber * Number(this.pageSize);
    const end = (pageNumber + 1) * Number(this.pageSize);

    let items = this.table.filter((item) =>
      item.name.includes(this.searchQuery)
    );

    if (this.selectedBlueprint) {
      items = items.filter((item) => item.blueprint === this.selectedBlueprint);
    }

    return this.sortItems(items).slice(start, end);
  }

  go(path: string): void {
    this.router.navigate([path]);
  }

  canGoBack() {
    return this.currentPage > 0;
  }

  canGoForward(): boolean {
    return this.getItemsForPage(this.currentPage + 1).length > 0;
  }

  nextPage() {
    this.currentPage++;
  }

  previousPage() {
    this.currentPage--;
  }
}
