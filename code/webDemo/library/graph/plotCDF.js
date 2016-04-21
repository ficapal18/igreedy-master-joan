//lineChart
function drawLinesChart() {
//xScale: d3.time.scale().clamp(true) cut data out of range
    nv.addGraph(function () {
        var chart = nv.models.lineChart()
        .interpolate("step-after") 
        .useInteractiveGuideline(true)
        .x(function(d) { return d[1] })
        .y(function(d) { return d[0]})
        .yDomain([0,1])
        .duration(300)
        .xScale(d3.scale.log())
        .color(d3.scale.category10().range())
        .showLegend(true)       
        .showYAxis(true)        
        .showXAxis(true);

         chart.xAxis     //Chart x-axis settings
              .axisLabel('Radius [km](ms)')
              .tickValues([1,10,100,1000,6371])
              .tickFormat(function (d) {
                    return  d + "\t(" + d/100+")";
                });

         chart.yAxis     //Chart x-axis settings
              .axisLabel('CDF')

        d3.select("#chartRtt svg")
            .datum(dataCDFRtt)
            .transition().duration(350)
            .call(chart);
       //Update the chart when window resizes.
        nv.utils.windowResize(function() { chart.update() });
        return chart;
    });

    nv.addGraph(function () {
        var chart = nv.models.lineChart()
        .interpolate("step-after") 
        .x(function(d) { return d[1] })
        .y(function(d) { return d[0]})
        .yDomain([0,1])
        .color(d3.scale.category10().range())
        .showLegend(true)       
        .showYAxis(true)        
        .showXAxis(true);

         chart.xAxis     //Chart x-axis settings
              .axisLabel('Hop')

         chart.yAxis     //Chart x-axis settings
              .axisLabel('CDF')
        d3.select("#chartTtl svg")
            .datum(dataCDFTtl)
            .transition().duration(350)
            .call(chart);
        return chart;
    });
}

//Donut chart
function drawPie(div,file) {
    nv.addGraph(function () {
        var chart = nv.models.pieChart()
            .x(function (d) { return d.label })
            .y(function (d) { return d.value })
            .showLabels(true)

            .labelType("percent")
            .donut(true)
            .donutRatio(0.35);

        d3.select("#" + div + " svg")
            .datum(file)
            .transition().duration(350)
            .call(chart);

        return chart;
    });
}
