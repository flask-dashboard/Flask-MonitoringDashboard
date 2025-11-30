import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AppConfigurationService {
  private _baseUrl = 'http://127.0.0.1:4200/dashboard/';
  constructor() {}

  public get baseUrl() {
    return this._baseUrl;
  }

  public constructPath(...path: string[]): string {
    return this._baseUrl + path.reduce((prev, curr) => prev + curr + '/');
  }
}
