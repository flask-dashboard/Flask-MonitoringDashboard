import { ExceptionService } from 'src/app/service/exception/exception.service';
import { HighlightService } from './../../../service/highlight.service';
import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  ViewChild,
} from '@angular/core';
import { take } from 'rxjs';

@Component({
  selector: 'app-syntax-highlight',
  templateUrl: './syntax-highlight.component.html',
  styleUrls: ['./syntax-highlight.component.css'],
  standalone: false,
})
export class SyntaxHighlightComponent implements AfterViewInit {
  @Input() public line_number!: number;
  @Input() public file_path!: string;
  @Input() public full_file_path!: string;
  @Input() public function_name!: string;
  @Input() public function_start_line_number!: number;
  @Input() public function_definition_id!: number;
  public code: string | null = null;
  private _codeEmitter: EventEmitter<string> = new EventEmitter();

  @ViewChild('codeElement') codeElement!: ElementRef;
  constructor(
    private readonly highlightService: HighlightService,
    private readonly exceptionService: ExceptionService
  ) {}

  ngAfterViewInit(): void {
    this._codeEmitter
      .asObservable()
      .pipe(take(1))
      .subscribe((code) => {
        this.code = code;

        setTimeout(() => {
          if (this.codeElement && this.codeElement.nativeElement) {
            this.highlightService.higlightElement(
              this.codeElement.nativeElement
            );
          }
        }, 0);
      });
  }

  fetchCode(): void {
    if (!this.code)
      this.exceptionService
        .getFunctionCode(this.function_definition_id)
        .pipe(take(1))
        .subscribe((code) => {
          this._codeEmitter.emit(code);
        });
  }
}
