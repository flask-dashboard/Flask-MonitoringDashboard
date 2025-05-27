export interface Requests {
  name: string;
  values: number[];
}

export interface HourlyLoad {
  days: Date[];
  data: number[][];
}
