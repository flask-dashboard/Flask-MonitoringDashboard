export interface DateInterval {
  from: Date;
  to: Date;
}

export interface TimestampInterval {
  from: number;
  to: number;
}

export interface ReportInterval {
  comparison: DateInterval;
  baseline: DateInterval;
}

export function DateIntervalToTimestampInterval(
  interval: DateInterval,
  milliConv?: boolean
): TimestampInterval {
  if (milliConv) {
    return {
      from: interval.from.getTime() / 1000,
      to: interval.to.getTime() / 1000,
    };
  }
  return {
    from: interval.from.getTime(),
    to: interval.to.getTime(),
  };
}

export enum AnswerType {
  MEDIAN_LATENCY = 'MEDIAN_LATENCY',
  STATUS_CODE_DISTRIBUTION = 'STATUS_CODE_DISTRIBUTION',
}

export interface IAnswer {
  type: AnswerType;
}

export interface MedianLatencyAnswer {
  baseline_median: number;
  is_significant: boolean;
  latencies_samples: {
    baseline: number[];
    comparison: number[];
  };
  median: number;
  percentual_diff: number;
  type: AnswerType;
}

export interface StatusCodeDistributionAnswer {
  is_significant: boolean;
  percentages: {
    baseline: number;
    comparison: number;
    percentage_diff: number;
    status_code: number;
  }[];
  type: AnswerType;
}

export interface Summary {
  endpoint_id: number;
  endpoint_name: string;
  answers: IAnswer[];
  has_anything_significant: boolean;
}
