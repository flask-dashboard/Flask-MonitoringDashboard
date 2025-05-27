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
