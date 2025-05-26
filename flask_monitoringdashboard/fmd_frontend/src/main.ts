/// <reference types="@angular/localize" />
import 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import 'prismjs/plugins/line-highlight/prism-line-highlight';

declare var Prism: any;

import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch((err) => console.error(err));
