app.service('plotlyService', function (formService) {
    let layout = {
        height: 600,
        margin: {l: 200}
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
            colorscale: 'YIOrRd',
            reversescale: true,
            type: 'heatmap'
        }], $.extend({}, layout, layout_ext));
    };

    this.chart = function (data, layout_ext) {
        formService.isLoading = false;
        Plotly.newPlot('chart', data, $.extend({}, layout, layout_ext), options);
    }
});