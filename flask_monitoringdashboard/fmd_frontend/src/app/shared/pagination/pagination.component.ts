import { NgFor } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

export interface PaginationDetails {
  offset: number;
  perPage: number;
  page: number;
  total: number;
}

@Component({
  selector: 'app-pagination',
  templateUrl: './pagination.component.html',
  styleUrls: ['./pagination.component.css'],
  imports: [NgFor],
})
export class PaginationComponent implements OnInit {
  @Input() paginationConfig!: PaginationDetails;
  @Input() name!: string;
  @Input() onReload?: (() => void) | undefined;
  @Output() onPageChange: EventEmitter<PaginationDetails> = new EventEmitter();
  constructor() {}

  ngOnInit() {}

  maxPages(): number {
    return Math.ceil(
      this.paginationConfig.total / this.paginationConfig.perPage
    );
  }

  getLeft(): number {
    return (this.paginationConfig.page - 1) * this.paginationConfig.perPage;
  }

  getRight(): number {
    return Math.min(
      this.paginationConfig.total,
      this.getLeft() + this.paginationConfig.perPage
    );
  }

  getPages(): (string | number)[] {
    let left = this.paginationConfig.page - 1;
    let right = this.paginationConfig.page + 1;
    let range = [];

    if (left <= 0) {
      right -= left - 1;
      left = 1;
    }
    if (right > this.maxPages()) {
      right = this.maxPages();
    }

    if (left == 2) {
      range.push(1);
    } else if (left == 3) {
      range.push(1, 2);
    } else if (left > 3) {
      range.push(1, '...');
    }

    for (let i = left; i <= right; i++) {
      range.push(i);
    }
    if (this.maxPages() - right > 2) {
      range.push('...', this.maxPages());
    } else if (this.maxPages() - right == 2) {
      range.push(this.maxPages() - 1, this.maxPages());
    } else if (this.maxPages() - right == 1) {
      range.push(this.maxPages());
    }
    return range;
  }

  getFirstPage(): string | number {
    const pages = this.getPages();
    return pages.length > 0 ? pages[0] : this.paginationConfig.page;
  }

  getLastPage(): string | number {
    const pages = this.getPages();
    return pages.length > 0
      ? pages[pages.length - 1]
      : this.paginationConfig.page;
  }

  goto(idx: number | string): void {
    if (typeof idx === 'number') {
      this.paginationConfig.page = idx;
      this.paginationConfig.offset = this.getLeft();
      this.onPageChange.emit(this.paginationConfig);
      if (this.onReload) this.onReload();
    }
  }
}
