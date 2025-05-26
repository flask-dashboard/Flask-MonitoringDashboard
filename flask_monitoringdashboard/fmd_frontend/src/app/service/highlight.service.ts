import { Injectable } from '@angular/core';
//import * as Prism from 'prismjs';
//import * as Python from 'prismjs';

declare var Prism: any;

@Injectable({
  providedIn: 'root',
})
export class HighlightService {
  constructor() {}

  highlightString(code: string): string {
    return Prism.highlight(code, Prism.languages['python']);
  }

  higlightElement(elm: Element): void {
    Prism.highlightElement(elm);
  }

  higlightAllUnder(parent: ParentNode): void {
    Prism.highlightAllUnder(parent);
  }
}
