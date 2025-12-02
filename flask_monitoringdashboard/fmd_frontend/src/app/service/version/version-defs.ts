export interface EndpointVersion {
  date: Date;
  version: string;
}

export interface EndpointUserVersion {
  data: number[][],
  versions: EndpointVersion[]
}
