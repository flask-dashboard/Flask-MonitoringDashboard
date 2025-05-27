import { Injectable } from '@angular/core';
import { Data, Datum, Layout, Root, TypedArray } from 'plotly.js';

declare var Plotly: any;

export interface HeatMap {
  root: Root;
  x: Datum[] | Datum[][] | TypedArray;
  y: Datum[] | Datum[][] | TypedArray;
  z: number[][];
  layout_ext: Partial<Layout>;
  hover_text: string | string[] | string[][] | undefined;
}

export interface Chart {
  root: Root;
  data: Partial<Data>[];
  layout_ext: Partial<Layout>;
}

@Injectable({
  providedIn: 'root',
})
export class PlotlyService {
  private _layout: Partial<Plotly.Layout> = {
    height: 600,
    margin: { l: 200 },
  };
  private _options: Partial<Plotly.Config> = {
    displaylogo: false,
    responsive: true,
  };
  constructor() {}

  chart({ root, data, layout_ext }: Chart): void {
    Plotly.newPlot(
      root,
      data,
      { ...layout_ext, ...this._layout },
      this._options
    );
  }

  heatmap({ root, x, y, z, layout_ext, hover_text }: HeatMap): void {
    this.chart({
      root,
      data: [
        {
          x: x,
          y: y,
          z: z.map((l) => l.map((i) => (i === 0 ? NaN : i))),
          colorscale: 'YIOrRd',
          reversescale: true,
          type: 'heatmap',
          text: hover_text as any,
          hoverinfo: hover_text === undefined ? undefined : 'text',
        },
      ],
      layout_ext: { ...layout_ext, ...this._layout },
    });
  }
}
