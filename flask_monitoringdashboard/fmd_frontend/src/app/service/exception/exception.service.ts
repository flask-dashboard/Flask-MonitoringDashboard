import { Injectable } from '@angular/core';
import { FmdClientService } from '../FmdClient.service';
import { Observable, of, tap } from 'rxjs';
import { ExceptionDetails, ExceptionGroup } from './exception-defs';

@Injectable({
  providedIn: 'root',
})
export class ExceptionService {
  private functions: Map<number, string> = new Map();

  constructor(private readonly client: FmdClientService) {}

  getNumberOfExceptions(id?: number): Observable<number> {
    return this.client.get(
      `api/num_exceptions${id !== undefined ? '/' + id : ''}`
    );
  }

  getExceptionDetails(
    id: number,
    offset: number,
    perPage: number
  ): Observable<ExceptionDetails[]> {
    return this.client.get(
      `api/detailed_exception_occurrence/${id}/${offset}/${perPage}`
    );
  }

  getFunctionCode(id: number): Observable<string> {
    const code = this.functions.get(id);
    if (code) return of(code);
    return this.client
      .get<string>(`api/function_code/${id}`)
      .pipe(tap((code) => this.functions.set(id, code)));
  }

  getExceptionGroups(
    offset: number,
    perPage: number
  ): Observable<ExceptionGroup[]> {
    return this.client.get(`api/exception_occurrence/${offset}/${perPage}`);
  }

  deleteExceptionByStackTraceId(id: number): Observable<void> {
    return this.client.delete(`api/exception_occurrence/${id}`);
  }
}
