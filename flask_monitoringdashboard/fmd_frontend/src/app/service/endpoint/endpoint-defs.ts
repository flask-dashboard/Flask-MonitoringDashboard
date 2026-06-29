export interface EndpointInfo {
  id: number;
  color: string;
  methods: string[];
  endpoint: string;
  rules: string[];
  'monitor-level': number;
  url: string;
  total_hits: number;
}

export interface Hit {
  name: string;
  hits: number;
}

export interface ApiPerformance {
  name: string;
  values: number[];
}

export interface VersionIpData {
  versions: { version: string; date: string }[];
  data: number[][];
}
