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
            if (!isNaN(d.data.value)) {
                return '0' + d.data.value;
            }
            return d.data.value;
        });
    function formatContent(el) {
        return categoryName + ": " + el.data.value + "<br>" + "Number: " + el.value;

    }

    bindTooltip(slice, id, formatContent);

}
function makeBarChart(dataset, id, title, categoryName, rotateLabel) {
    if (dataset.length === 0) {
        return false;
    }
    var margin = {top: 70, right: 20, bottom: 130, left: 40},
        w = 550 - margin.left - margin.right,
        h = 450 - margin.top - margin.bottom;
    var color = d3.scale.category20c();

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, w], 0.1);
    var y = d3.scale.linear()
        .range([h, 0]);
    var y2 = d3.scale.linear()
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
    y2.domain([0, d3.max(dataset, function (d) {
        return d.count;
    })]);


    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");
    var yAxis = d3.svg.axis()
        .scale(y2)
        .orient("left");
    yAxis.tickFormat(d3.format("d"));

    var svgAxis = graph.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0, " + h + ")")
        .call(xAxis);
    if (rotateLabel === true) {
        svgAxis.selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", function (d) {
                return "rotate(-65)";
            });
    }
    svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .call(yAxis);
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
    var fullWidth = 1000;

    var focusHeight = 500;
    var contextHeight = 100;
    var fullHeight = focusHeight + contextHeight;
    var margin = {top: 100, right: 40, bottom: 60, left: 40},
        width = fullWidth - margin.left - margin.right,
        height = focusHeight - margin.top - margin.bottom;

    var margin2 = {top: 20, right: 40, bottom: 20, left: 40};
    var height2 = contextHeight - margin2.top - margin2.bottom;
    var formatDate = d3.time.format("%B %Y");
    var values = _.map(dataset, function (el) {
        return {
            "value": el.value,
            "date": new Date(el.year, el.month - 1, 1)
        };
    });
    var maxValue = _.max(values, function (el) {
        return el.value;
    }).value;

    var svg = d3.select(id).append("svg")
        .attr("width", fullWidth)
        .attr("height", fullHeight);
    var extents = d3.extent(values, function (d) {
        return d.date;
    });


    var x = d3.time.scale().domain(extents).rangeRound([0, width]);

    var y = d3.scale.linear().domain([0, maxValue]).range([0, height]);
    var y2 = d3.scale.linear().domain([0, maxValue]).range([height, 0]);

    var xContext = d3.time.scale().domain(extents).rangeRound([0, width]);
    var yContext = d3.scale.linear().domain([0, maxValue]).range([0, height2]);
    // define the y axis
    var yAxis = d3.svg.axis()
        .orient("left")
        .scale(y2);

    // define the focus x axis
    var xAxis = d3.svg.axis()
        .orient("bottom")
        .scale(x);
    xAxis.ticks(d3.time.month, 1);
    xAxis.tickFormat(d3.time.format("%b %y"));

    // define the context x axis
    var xAxis2 = d3.svg.axis()
        .orient("bottom")
        .scale(x);

    //  focus chart function
    var line = d3.svg.line()
        .x(function (d) {
            return x(d.date);
        })
        .y(function (d) {
            return -1 * y(d.value);
        });

    //  context chart function
    var line2 = d3.svg.line()
        .x(function (d) {
            return x(d.date);
        })
        .y(function (d) {
            return -1 * yContext(d.value);
        });

    // brush for navigation
    var brush = d3.svg.brush()
        .x(xContext)
        .on("brush", brushed);

    // creating 2 chart groups
    var focus = svg.append("g")
        .attr("class", "focus")
        .attr("transform", "translate(" + margin.left + ", " + (height + margin.top) + ")");
    var context = svg.append("g")
        .attr("class", "context")
        .attr("transform", "translate(" + margin2.left + "," + (focusHeight + contextHeight - margin2.bottom) + ")");

    // concrete chart drawing
    focus
        .append("path")
        .datum(values)
        .attr("d", line(values))
        .attr('class', 'linechart');

    // adding dots
    var circle = focus.selectAll(".circle")
        .data(values)
        .enter().append("circle")
        .attr("r", 5)
        .attr("cx", function (d) {
            return x(d.date);
        })
        .attr("cy", function (d) {
            return -1 * y(d.value);
        }).attr('class', 'circle');

    // add a rect to hide chart on the left
    focus.append("g")
        .attr("transform", "translate(" + -100 + "," + -height + ")")
        .append("rect")
        .attr('fill', '#f2f0f0')
        .attr('height', height)
        .attr('width', 100);

    // add y axis
    focus.append("g")
        .attr("transform", "translate(" + 0 + "," + -height + ")")
        .attr("class", "y axis")
        .call(yAxis);

    // add x axis and rotate labels
    focus.append("g")
        .attr("class", "x axis")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", function (d) {
            return "rotate(-65)";
        });
    focus.append("g")
    // draw context chart
    context.append("path")
        .datum(values)
        .attr('class', 'linechart')
        .attr("d", line2(values));
    // add context x axis
    context.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(" + 0 + "," + (0) + ")")
        .call(xAxis2);

    // adding brush
    context.append("g")
        .attr("class", "x brush")
        .call(brush)
        .selectAll("rect")
        .attr("y", -height2)
        .attr("height", height2);
    // adding chart title
    addTitle(svg, title, width, margin.top);

    // tooltips instanciation
    var tooltip = d3.select(id).append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    function formatContent(el) {
        return formatDate(el.date) + "<br/>Number: " + el.value;
    }

    bindTooltip(circle, id, formatContent);

    // brush callback function
    function brushed() {
        x.domain(brush.empty() ? xContext.domain() : brush.extent());
        focus.select(".linechart").attr("d", line);
        focus.select(".x.axis").call(xAxis).selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", function (d) {
                return "rotate(-65)";
            });
        focus.selectAll(".circle")
            .attr("cx", function (d) {
                return x(d.date);
            });
    }
}
