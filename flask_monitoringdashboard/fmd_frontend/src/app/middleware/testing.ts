import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class LoggingInterceptor implements HttpInterceptor {
  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    console.log('*** Outgoing Request Check ***');
    console.log('URL:', request.url);
    console.log(
      'Headers:',
      request.headers.keys().map((key) => `${key}: ${request.headers.get(key)}`)
    );
    console.log('******************************');
    const apiRequest = request.clone({
      withCredentials: true,
    });

    return next.handle(apiRequest);
  }
}
