export interface OverviewDto {
  id: number;
  name: string;
  blueprint: string;
  monitor: number;
  color: string;
  'hits-today': number;
  'hits-today-errors': number;
  'hits-week': number;
  'hits-week-errors': number;
  'hits-overall': number;
  'median-today': number;
  'median-week': number;
  'median-overall': number;
  'last-accessed': string;
  exceptions: number;
}
