export interface RequestInfo {
  name: string;
  values: number[];
}

export interface RequestsData {
  data: RequestInfo[];
  days: Date;
}

export interface HourlyLoad {
  days: Date[];
  data: number[][];
}
