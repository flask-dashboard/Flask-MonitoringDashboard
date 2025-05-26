import { NgIf, CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewEncapsulation,
} from '@angular/core';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';
import { NgbCollapse } from '@ng-bootstrap/ng-bootstrap';

export interface MenuConfig {
  path: string;
  text: string;
  formatArgs?: any[];
}

@Component({
  selector: 'app-menu-segment',
  templateUrl: './menu-segment.component.html',
  styleUrls: ['./menu-segment.component.css'],
  standalone: true,
  encapsulation: ViewEncapsulation.None,
  imports: [NgIf, CommonModule, NgbCollapse, FontAwesomeModule, RouterModule],
})
export class MenuSegmentComponent implements OnInit {
  //@Output() toggleSegment: EventEmitter<boolean> = new EventEmitter();
  @Input() expanded!: boolean;
  @Input() menuConfig!: MenuConfig[];
  public chevronDown = faChevronDown;
  public chevronUp = faChevronUp;

  constructor() {}

  ngOnInit() {}

  format(path: string, args?: any[]): string {
    if (!args) return path;
    return path.replace(/{(\d+)}/g, (match: string, num: any) => {
      return typeof num === 'number' && args[num] !== undefined
        ? args[num]
        : match;
    });
  }
}
