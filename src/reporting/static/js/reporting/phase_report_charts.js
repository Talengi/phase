function addTitle(elt, title, width, marginTop) {
    elt.append("text")
        .attr("x", (width / 2))
        .attr("y", marginTop / 2)
        .attr("text-anchor", "middle")
        .style("font-size", "24px")
        .text(title);
}
function bindTooltip(elt, id, formatContent) {
    var tooltip = d3.select(id).append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    elt.on('mouseover', function (el) {
        d3.select(this).transition()
            .duration(200).style("opacity", 0.9);
        tooltip.transition()
            .duration(200)
            .style("opacity", 0.9);
        tooltip.html(formatContent(el))
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 10) + "px");
    });

    elt.on('mousemove', function (el) {
        tooltip.style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 10) + "px");
    });

    elt.on("mouseout", function (d) {
        d3.select(this).transition()
            .duration(200).style("opacity", 1);
        tooltip.transition()
            .duration(200)
            .style("opacity", 0);
    });
}
function makePie(dataset, id, title, categoryName) {
    if (dataset.length === 0) {
        return false;
    }
    var margin = {top: 70, right: 20, bottom: 30, left: 40},
        w = 500 - margin.left - margin.right,
        h = 400 - margin.top - margin.bottom;
    var color = d3.scale.category20c();
    var radius = Math.min(w, h) / 2;
    var arc = d3.svg.arc()
        .outerRadius(radius)
        .innerRadius(0);
;
    var pie = d3.layout.pie()
        .sort(null)
        .value(function (d) {
            return d.count;
        });
    var svg = d3.select(id).append("svg")
        .attr("width", w + margin.left + margin.right)
        .attr("height", h + margin.top + margin.bottom);

    addTitle(svg, title, w, margin.top);

    var g = svg.append("g")
        .attr("transform", "translate(" + (w / 2 + margin.left) +
            "," + (h / 2 + margin.top) + ")").selectAll('g')
        .data(pie(dataset))
        .enter();

    var slice = g.append('path')
        .attr('d', arc)
        .attr('class', 'slice')
        .attr('fill', function (d) {
            return color(d.data.value);
        });

    var tooltip = d3.select(id).append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);


    g.append("text")
        .attr("transform", function (d) {
            return "translate(" + arc.centroid(d) + ")";
        })
        .attr("text-anchor", "middle")
        .text(function (d) {
            if (!isNaN(d.data.value)){
                return '0'+ d.data.value;
            }
            return d.data.value;
        });
    function formatContent(el) {
        return categoryName + ": " + el.data.value + "<br>" + "Number: " + el.value;

    }

    bindTooltip(slice, id, formatContent);

}
function makeBarChart(dataset, id, title, categoryName) {
    if (dataset.length === 0) {
        return false;
    }
    var margin = {top: 70, right: 20, bottom: 30, left: 40},
        w = 500 - margin.left - margin.right,
        h = 350 - margin.top - margin.bottom;
    var color = d3.scale.category20c();

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, w], 0.1);
    var y = d3.scale.linear()
        .range([h, 0]);
    var svg = d3.select(id).append("svg")
        .attr("width", w + margin.left + margin.right)
        .attr("height", h + margin.top + margin.bottom);
    addTitle(svg, title, w, margin.top);
    var graph = svg.append('g').attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

    var sum = 0;
    dataset.forEach(function (d) {
        sum += d.count;
    });
    x.domain(dataset.map(function (d) {
        return d.value;
    }));
    y.domain([0, d3.max(dataset, function (d) {
        return d.count / sum;
    })]);
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    graph.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0, " + h + ")")
        .call(xAxis);

    var b = graph.selectAll(".bar")
        .data(dataset)
        .enter();

    var bar = b.append("rect")
        .attr("class", "bar")
        .attr("x", function (d) {
            return x(d.value);
        })
        .attr("width", x.rangeBand())
        .attr("y", function (d) {
            return y(d.count / sum);
        })
        .attr("height", function (d) {
            return h - y(d.count / sum);
        })
        .attr("fill", function (d) {
            return color(d.value);
        });

    function formatContent(el) {
        return categoryName + ": " + el.value + "<br>" + "Number: " + el.count;

    }

    bindTooltip(bar, id, formatContent);


}
function makeLineChart(dataset, id, title, categoryName) {
    if (dataset.length === 0) {
        return false;
    }
    var width = 1000;
    var height = 400;
    var margin = {top: 100, right: 40, bottom: 30, left: 40},
        w = width - margin.left - margin.right,
        h = height - margin.top - margin.bottom;
    var formatDate = d3.time.format("%B %Y");
    var values = _.map(dataset, function (el) {
        return {
            "value": el.value,
            "date": new Date(el.year, el.month - 1, 1)
        };
    });
    var firstDate = values[0].date;
    var lastElt = values[values.length - 1];
    var lastDate = lastElt.date;
    var maxValue = _.max(values, function (el) {
        return el.value;
    }).value;


    var svg = d3.select(id).append("svg")
        .attr("width", width)
        .attr("height", height);

    addTitle(svg, title, w, margin.top);
    var g = svg.append("g")
        .attr("transform", "translate(" + (10 + margin.left) + ", " + (h + margin.top) + ")");

    var y = d3.scale.linear().domain([0, maxValue]).range([0, h]);
    var y2 = d3.scale.linear().domain([0, maxValue]).range([h, 0]);


    var x = d3.time.scale().domain([firstDate, lastDate]).rangeRound([0, w]);

    // define the y axis

    var yAxis = d3.svg.axis()
        .orient("left")
        .scale(y2);

    // define the x axis
    var xAxis = d3.svg.axis()
        .orient("bottom")
        .scale(x);

    xAxis.ticks(d3.time.month, 1);
    xAxis.tickFormat(d3.time.format("%m/%Y"));

    var line = d3.svg.line()
        .x(function (d) {
            return x(d.date);
        })
        .y(function (d) {
            return -1 * y(d.value);
        });
    svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .call(yAxis);
    svg.append("g")
        .attr("class", "xaxis")
        .attr("transform", "translate(" + margin.left + "," + (h + margin.top ) + ")")
        .call(xAxis);
    var tooltip = d3.select(id).append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    g.append("path").attr("d", line(values)).attr('class', 'linechart');
    var circle = g.selectAll("circle")
        .data(values)
        .enter().append("circle")
        .attr("r", 5)
        .attr("cx", function (d) {
            return x(d.date);
        })
        .attr("cy", function (d) {
            return -1 * y(d.value);
        }).attr('class', 'circle');


    function formatContent(el) {
        return formatDate(el.date) + "<br/>Number: " + el.value;

    }

    bindTooltip(circle, id, formatContent);

}
