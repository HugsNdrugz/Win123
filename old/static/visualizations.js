// D3.js Visualizations
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        createMonthlyMessagesChart(stats);
        createActiveUsersChart(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function createMonthlyMessagesChart(data) {
    const margin = {top: 20, right: 20, bottom: 30, left: 40};
    const width = 500 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Clear previous chart
    d3.select("#monthly-messages-chart").html("");

    const svg = d3.select("#monthly-messages-chart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // X axis
    const x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);

    // Y axis
    const y = d3.scaleLinear()
        .range([height, 0]);

    x.domain(data.map(d => d.month));
    y.domain([0, d3.max(data, d => d.message_count)]);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add bars
    svg.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.month))
        .attr("width", x.bandwidth())
        .attr("y", d => y(d.message_count))
        .attr("height", d => height - y(d.message_count))
        .attr("fill", "#0084ff");

    // Add title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 0)
        .attr("text-anchor", "middle")
        .text("Monthly Message Count");
}

function createActiveUsersChart(data) {
    const margin = {top: 20, right: 20, bottom: 30, left: 40};
    const width = 500 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Clear previous chart
    d3.select("#active-users-chart").html("");

    const svg = d3.select("#active-users-chart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create line generator
    const line = d3.line()
        .x(d => x(d.month))
        .y(d => y(d.unique_senders));

    // X axis
    const x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);

    // Y axis
    const y = d3.scaleLinear()
        .range([height, 0]);

    x.domain(data.map(d => d.month));
    y.domain([0, d3.max(data, d => d.unique_senders)]);

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add line
    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#0084ff")
        .attr("stroke-width", 2)
        .attr("d", line);

    // Add title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 0)
        .attr("text-anchor", "middle")
        .text("Active Users Over Time");
}
