import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AppConfigurationService } from './app-configuration.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class FmdClientService {
  constructor(
    private readonly client: HttpClient,
    private readonly config: AppConfigurationService
  ) {}

  get<T>(path: string): Observable<T> {
    return this.client.get<T>(this.config.constructPath(path));
  }

  post<T>(path: string, body: any): Observable<T> {
    return this.client.post<T>(this.config.constructPath(path), body);
  }
}
