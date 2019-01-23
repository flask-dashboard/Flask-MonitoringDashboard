app.service('plotlyService', function () {
    let layout = {
        height: 600,
    };
    let options = {
        displaylogo: false,
        responsive: true
    };

    this.heatmap = function (x, y, z, layout_ext) {
        this.chart([{
            x: x,
            y: y,
            z: z.map(l => l.map(i => i == 0 ? NaN : i)),
            type: 'heatmap'
        }], $.extend({}, layout, layout_ext));
    };

    this.chart = function (data, layout_ext) {
        Plotly.newPlot('chart', data, $.extend({}, layout, layout_ext), options);
    }
});