from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def dag_dependencies_graph():
    """Interactive DAG Dependencies Graph"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DAG Dependencies Graph</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #F5F5F5;
                min-height: 100vh;
            }
            
            .header {
                text-align: center;
                color: #000000;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 600;
                color: #000000;
            }
            
            .graph-container {
                background: #FFFFFF;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                border: 2px solid #FFFFFF;
                margin: 0 auto;
                max-width: 95%;
                height: 80vh;
                overflow: hidden;
            }
            
            .controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                flex-wrap: wrap;
                gap: 15px;
            }
            
            .search-container {
                display: flex;
                align-items: center;
                gap: 10px;
                flex: 1;
                min-width: 300px;
            }
            
            .search-input {
                flex: 1;
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            
            .search-input:focus {
                outline: none;
                border-color: #007bff;
            }
            
            .search-help {
                font-size: 12px;
                color: #6c757d;
                white-space: nowrap;
            }
            
            .clear-btn {
                padding: 8px 12px;
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s ease;
            }
            
            .clear-btn:hover {
                background: #545b62;
            }
            
            .legend {
                display: flex;
                gap: 20px;
                align-items: center;
                flex-wrap: wrap;
            }
            
            .legend-item {
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 0.9em;
            }
            
            .legend-circle {
                width: 12px;
                height: 12px;
                border-radius: 50%;
            }
            
            .reset-btn {
                padding: 8px 16px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s ease;
            }
            
            .reset-btn:hover {
                background: #0056b3;
            }
            
            #graph {
                width: 100%;
                height: calc(100% - 80px);
                background: #F5F5F5;
                border: 3px solid #FFFFFF;
                border-radius: 8px;
            }
            
            .node {
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .node:hover {
                stroke-width: 3px;
            }
            
            .node.filtered {
                opacity: 0.3;
            }
            
            .node.highlighted {
                stroke: #ff6b6b;
                stroke-width: 4px;
                filter: drop-shadow(0 0 8px rgba(255, 107, 107, 0.6));
            }
            
            .link.filtered {
                opacity: 0.2;
            }
            
            .node-text.filtered {
                opacity: 0.3;
            }
            
            .node-text {
                font-size: 14px;
                fill: #000000;
                text-anchor: middle;
                dominant-baseline: middle;
                pointer-events: none;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            }
            
            .link {
                stroke: #999;
                stroke-opacity: 0.8;
                stroke-width: 2;
                fill: none;
                marker-end: url(#arrowhead);
            }
            
            .link.dataset {
                stroke: #28a745;
                stroke-dasharray: 5,5;
                stroke-width: 2;
                marker-end: url(#arrowhead-dataset);
            }
            
            .link.trigger {
                stroke: #ffc107;
                stroke-width: 3;
                marker-end: url(#arrowhead-trigger);
            }
            
            .tooltip {
                position: absolute;
                padding: 8px 12px;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                border-radius: 6px;
                font-size: 12px;
                pointer-events: auto;
                z-index: 1000;
                max-width: 250px;
                line-height: 1.4;
            }
            
            .tooltip a {
                color: #87ceeb;
                text-decoration: underline;
            }
            
            .tooltip a:hover {
                color: #add8e6;
            }
            
            .footer {
                text-align: center;
                margin-top: 20px;
                padding: 15px;
                color: #666;
                font-size: 14px;
            }
            
            .footer p {
                margin: 0;
                color: #666;
            }
            
            .footer a {
                color: #007bff;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s ease;
            }
            
            .footer a:hover {
                color: #0056b3;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔗 DAG Dependencies Graph</h1>
            <p>Interactive visualization of DAG dependencies, datasets, and triggers</p>
        </div>
        
        <div class="graph-container">
            <div class="controls">
                <div class="search-container">
                    <input type="text" class="search-input" id="searchInput" 
                           placeholder="Search DAGs (e.g., load_ticket_sales+1, 2+transform_customer_sentiment, @exact_name)" 
                           oninput="handleSearch(this.value)">
                    <div class="search-help">+upstream | downstream+ | N+upstream | downstream+N | @exact</div>
                    <button class="clear-btn" onclick="clearSearch()">Clear</button>
                </div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-circle" style="background: #F5E6D3; border: 1px solid #FFFFFF;"></div>
                        <span>Scheduled</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-circle" style="background: #E8F5E9; border: 1px solid #FFFFFF;"></div>
                        <span>Dataset</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-circle" style="background: #FBE4E0; border: 1px solid #FFFFFF;"></div>
                        <span>Manual</span>
                    </div>
                </div>
                <button class="reset-btn" onclick="resetGraph()">Reset View</button>
            </div>
            <svg id="graph"></svg>
        </div>
        
        <div class="tooltip" id="tooltip" style="display: none;"></div>
        
        <div class="footer">
            <p>Made by <a href="https://ponder.co/" target="_blank" rel="noopener noreferrer">Ponder</a> and <a href="https://www.linkedin.com/in/egorseno/" target="_blank" rel="noopener noreferrer">Egor Tarasenko</a></p>
        </div>
        
        <script>
            // Global variable to store DAG data (will be loaded from API)
            let dagData = {
                nodes: [],
                links: []
            };
            
            // Load DAG data from API
            async function loadDAGData() {
                try {
                    console.log('Loading DAG data from Airflow API...');
                    const response = await fetch('/dags_dependencies/api/dag-dependencies');
                    
                    if (!response.ok) {
                        throw new Error(`API request failed: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('Received DAG data:', data);
                    
                    dagData = {
                        nodes: data.nodes || [],
                        links: data.links || []
                    };
                    
                    // Show API status in the header
                    if (data.success) {
                        let statusText = `Interactive visualization of ${data.total_dags} DAGs from DagBag`;
                        if (data.import_errors > 0) {
                            statusText += ` (${data.import_errors} import errors)`;
                        }
                        document.querySelector('.header p').innerHTML = statusText;
                    } else {
                        document.querySelector('.header p').innerHTML = 
                            `Interactive visualization (DagBag error: ${data.error || 'Unknown'})`;
                    }
                    
                    // Initialize the graph after data is loaded
                    initializeGraph();
                    
                } catch (error) {
                    console.error('Error loading DAG data:', error);
                    
                    document.querySelector('.header p').innerHTML = 
                        `Interactive visualization (API error: ${error.message})`;
                    
                    // Don't initialize graph if no data
                }
            }
            
            const width = 1400;  // Increased width for rectangular nodes
            const height = 600;
            
            // Initialize the graph visualization
            function initializeGraph() {
                // Clear any existing graph
                d3.select("#graph").selectAll("*").remove();
                
                const svg = d3.select("#graph")
                    .attr("width", width)
                    .attr("height", height);
            
            // Add zoom and pan functionality
            const g = svg.append("g");
            
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", function(event) {
                    g.attr("transform", event.transform);
                });
            
            svg.call(zoom);
            
            // Add arrowhead markers
            const defs = svg.append("defs");
            
            // Default arrowhead
            defs.append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 90)  // Adjusted for larger rectangle edge (80 + 10)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
            
            // Dataset arrowhead (green)
            defs.append("marker")
                .attr("id", "arrowhead-dataset")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 90)  // Adjusted for larger rectangle edge (80 + 10)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#28a745");
            
            // Trigger arrowhead (yellow)
            defs.append("marker")
                .attr("id", "arrowhead-trigger")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 90)  // Adjusted for larger rectangle edge (80 + 10)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#ffc107");
            
            const tooltip = d3.select("#tooltip");
            
            // Hide tooltip when mouse leaves it
            tooltip.on("mouseleave", function() {
                tooltip.style("display", "none");
            });
            
            // Create hierarchical layout with crossing minimization
            function createHierarchicalLayout() {
                // Build dependency map
                const dependencyMap = new Map();
                const dependents = new Set();
                
                dagData.links.forEach(link => {
                    if (!dependencyMap.has(link.source)) {
                        dependencyMap.set(link.source, []);
                    }
                    dependencyMap.get(link.source).push(link.target);
                    dependents.add(link.target);
                });
                
                // Find root nodes (no dependencies)
                const rootNodes = dagData.nodes.filter(node => !dependents.has(node.id));
                
                // Calculate levels using topological sort
                const levels = new Map();
                const visited = new Set();
                
                function calculateLevel(nodeId) {
                    if (visited.has(nodeId)) return levels.get(nodeId) || 0;
                    visited.add(nodeId);
                    
                    let maxLevel = 0;
                    dagData.links.forEach(link => {
                        if (link.target === nodeId) {
                            const sourceLevel = calculateLevel(link.source);
                            maxLevel = Math.max(maxLevel, sourceLevel + 1);
                        }
                    });
                    
                    levels.set(nodeId, maxLevel);
                    return maxLevel;
                }
                
                // Calculate levels for all nodes
                dagData.nodes.forEach(node => calculateLevel(node.id));
                
                // Group nodes by level
                const levelGroups = new Map();
                dagData.nodes.forEach(node => {
                    const level = levels.get(node.id);
                    if (!levelGroups.has(level)) {
                        levelGroups.set(level, []);
                    }
                    levelGroups.get(level).push(node);
                });
                
                // Optimize node ordering within each level to minimize crossings
                function optimizeNodeOrdering() {
                    const maxLevel = Math.max(...levelGroups.keys());
                    
                    // Forward pass: optimize based on predecessors
                    for (let level = 1; level <= maxLevel; level++) {
                        if (levelGroups.has(level)) {
                            const nodes = levelGroups.get(level);
                            
                            // Calculate barycenter (average position of predecessors)
                            nodes.forEach(node => {
                                let totalPos = 0;
                                let count = 0;
                                
                                dagData.links.forEach(link => {
                                    if (link.target === node.id && levelGroups.has(level - 1)) {
                                        const sourceNode = levelGroups.get(level - 1).find(n => n.id === link.source);
                                        if (sourceNode && sourceNode.tempY !== undefined) {
                                            totalPos += sourceNode.tempY;
                                            count++;
                                        }
                                    }
                                });
                                
                                node.barycenter = count > 0 ? totalPos / count : Math.random() * 1000;
                            });
                            
                            // Sort by barycenter
                            nodes.sort((a, b) => a.barycenter - b.barycenter);
                            
                            // Assign temporary positions
                            nodes.forEach((node, index) => {
                                node.tempY = index;
                            });
                        }
                    }
                    
                    // Backward pass: optimize based on successors
                    for (let level = maxLevel - 1; level >= 0; level--) {
                        if (levelGroups.has(level)) {
                            const nodes = levelGroups.get(level);
                            
                            // Calculate barycenter (average position of successors)
                            nodes.forEach(node => {
                                let totalPos = 0;
                                let count = 0;
                                
                                dagData.links.forEach(link => {
                                    if (link.source === node.id && levelGroups.has(level + 1)) {
                                        const targetNode = levelGroups.get(level + 1).find(n => n.id === link.target);
                                        if (targetNode && targetNode.tempY !== undefined) {
                                            totalPos += targetNode.tempY;
                                            count++;
                                        }
                                    }
                                });
                                
                                node.barycenter = count > 0 ? totalPos / count : node.tempY || Math.random() * 1000;
                            });
                            
                            // Sort by barycenter
                            nodes.sort((a, b) => a.barycenter - b.barycenter);
                            
                            // Update temporary positions
                            nodes.forEach((node, index) => {
                                node.tempY = index;
                            });
                        }
                    }
                }
                
                // Run optimization multiple passes for better results
                for (let pass = 0; pass < 3; pass++) {
                    optimizeNodeOrdering();
                }
                
                // Position nodes based on optimized ordering
                const levelWidth = width / (levelGroups.size + 1);
                const nodeWidth = 160;
                const nodeHeight = 60;
                
                levelGroups.forEach((nodes, level) => {
                    const x = (level + 1) * levelWidth;
                    const verticalSpacing = Math.max(90, (height - 120) / (nodes.length + 1));
                    
                    // Sort nodes by their optimized positions
                    nodes.sort((a, b) => (a.tempY || 0) - (b.tempY || 0));
                    
                    nodes.forEach((node, index) => {
                        node.x = x;
                        node.y = 80 + (index + 1) * verticalSpacing;
                        node.fx = x; // Fix position
                        node.fy = node.y;
                        
                        // Clean up temporary variables
                        delete node.tempY;
                        delete node.barycenter;
                    });
                });
                
                console.log('Layout optimized for minimal edge crossings');
            }
            
            createHierarchicalLayout();
            
            const linkGroup = g.append("g").attr("class", "links");
            const nodeGroup = g.append("g").attr("class", "nodes");
            const textGroup = g.append("g").attr("class", "texts");
            
            const link = linkGroup
                .selectAll("path")
                .data(dagData.links)
                .enter().append("path")
                .attr("class", d => `link ${d.type}`)
                .on("mouseover", function(event, d) {
                    const sourceId = typeof d.source === 'string' ? d.source : d.source.id;
                    const targetId = typeof d.target === 'string' ? d.target : d.target.id;
                    let tooltipText = `${sourceId} → ${targetId}`;
                    if (d.type === "dataset") {
                        tooltipText += `\\nDataset: ${d.dataset}`;
                    } else if (d.type === "trigger") {
                        tooltipText += "\\nDAG Trigger";
                    }
                    tooltip.style("display", "block")
                        .html(tooltipText.replace(/\\n/g, "<br>"))
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                })
                .on("mouseout", function() {
                    tooltip.style("display", "none");
                });
            
            const node = nodeGroup
                .selectAll("rect")
                .data(dagData.nodes)
                .enter().append("rect")
                .attr("class", "node")
                .attr("width", 160)
                .attr("height", 60)
                .attr("rx", 12)
                .attr("ry", 12)
                .attr("fill", d => {
                    switch(d.type) {
                        case "scheduled": return "#F5E6D3";  // Light orange/tan for scheduled
                        case "dataset": return "#E8F5E9";   // Light green for dataset
                        default: return "#FBE4E0";          // Light pink/coral for manual
                    }
                })
                .attr("stroke", "#FFFFFF")
                .attr("stroke-width", 2)
                .on("click", function(event, d) {
                    event.stopPropagation();
                    // Use the correct Airflow URL format
                    const airflowUrl = `/dags/${d.id}`;
                    window.open(airflowUrl, '_blank');
                })
                .on("mouseover", function(event, d) {
                    d3.select(this).attr("stroke-width", 5);
                    const dagUrl = `/dags/${d.id}`;
                    tooltip.style("display", "block")
                        .html(`<strong>${d.id}</strong><br>Schedule: ${d.schedule}<br>URL: <a href="${dagUrl}" target="_blank" style="color: #87ceeb;">${dagUrl}</a><br>Click to view DAG`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                })
                .on("mouseout", function(event) {
                    d3.select(this).attr("stroke-width", 3);
                    // Delay hiding tooltip to allow clicking on links
                    setTimeout(() => {
                        if (!tooltip.node().matches(':hover')) {
                            tooltip.style("display", "none");
                        }
                    }, 100);
                });
            
            const text = textGroup
                .selectAll("text")
                .data(dagData.nodes)
                .enter().append("text")
                .attr("class", "node-text")
                .style("font-size", "11px")
                .style("font-weight", "600")
                .style("text-anchor", "middle")
                .style("dominant-baseline", "middle")
                .style("pointer-events", "none")
                .style("user-select", "none");
            
            // Add text using real DAG IDs
            text.each(function(d) {
                const textElement = d3.select(this);
                // Split long DAG names into multiple lines
                const words = d.id.split('_');
                if (words.length > 1) {
                    // Split into lines of 2 words each for better readability
                    const lines = [];
                    for (let i = 0; i < words.length; i += 2) {
                        lines.push(words.slice(i, i + 2).join('_'));
                    }
                    lines.forEach((line, i) => {
                        textElement.append("tspan")
                            .attr("x", 0)
                            .attr("dy", i === 0 ? "-0.4em" : "1.2em")
                            .style("font-size", "14px")
                            .style("font-weight", "600")
                            .style("fill", "#000000")
                            .text(line);
                    });
                } else {
                    textElement.text(d.id)
                        .style("font-size", "14px")
                        .style("font-weight", "600")
                        .style("fill", "#000000");
                }
            });
            
            // Position elements statically
            function updatePositions() {
                // Update links with straight lines
                link.attr("d", d => {
                    // Handle both string IDs and object references
                    const sourceId = typeof d.source === 'string' ? d.source : d.source.id;
                    const targetId = typeof d.target === 'string' ? d.target : d.target.id;
                    const sourceNode = dagData.nodes.find(n => n.id === sourceId);
                    const targetNode = dagData.nodes.find(n => n.id === targetId);
                    if (sourceNode && targetNode) {
                        return `M${sourceNode.x},${sourceNode.y}L${targetNode.x},${targetNode.y}`;
                    }
                    return "";
                });
                
                // Update nodes
                node
                    .attr("x", d => d.x - 80)  // Center the rectangle (width/2 = 160/2)
                    .attr("y", d => d.y - 30); // Center the rectangle (height/2 = 60/2)
                
                // Update text
                text
                    .attr("transform", d => `translate(${d.x}, ${d.y})`);
            }
            
            // Initial positioning
            updatePositions();
            
            } // End of initializeGraph function
            
            // Global functions that need to be accessible from HTML
            function resetGraph() {
                // Reset zoom only - need to access the svg from global scope
                const svg = d3.select("#graph");
                const zoom = d3.zoom().scaleExtent([0.1, 4]);
                svg.transition().duration(750).call(
                    zoom.transform,
                    d3.zoomIdentity
                );
            }
            
            // Search functionality - GLOBAL SCOPE
            let currentHighlighted = new Set();
            
            function handleSearch(query) {
                if (!query.trim()) {
                    clearSearch();
                    return;
                }
                
                const matches = parseSearchQuery(query);
                applyFilter(matches);
            }
            
            function parseSearchQuery(query) {
                const results = new Set();
                const terms = query.toLowerCase().split(/\\s+/).filter(t => t.length > 0);
                
                for (const term of terms) {
                    // Check range queries first (most specific pattern with multiple +)
                    if (term.includes('+') && /\\d/.test(term) && term.split('+').length >= 3) {
                        // Range query like 1+sales+2 or +sales+1
                        const matches = parseRangeQuery(term);
                        matches.forEach(id => results.add(id));
                    } else if (/^\\d+\\+/.test(term)) {
                        // N+dag_name - show dag and N levels upstream
                        const match = term.match(/^(\\d+)\\+(.+)$/);
                        if (match) {
                            const levels = parseInt(match[1]);
                            const dagName = match[2];
                            const matches = findDAGsWithUpstreamLevels(dagName, levels);
                            matches.forEach(id => results.add(id));
                        }
                    } else if (/\\+\\d+$/.test(term)) {
                        // dag_name+N - show dag and N levels downstream
                        const match = term.match(/^(.+)\\+(\\d+)$/);
                        if (match) {
                            const dagName = match[1];
                            const levels = parseInt(match[2]);
                            const matches = findDAGsWithDownstreamLevels(dagName, levels);
                            matches.forEach(id => results.add(id));
                        }
                    } else if (term.startsWith('+') && term.endsWith('+')) {
                        // +dag_name+ - show dag and all its upstream and downstream
                        const dagName = term.slice(1, -1);
                        const matches = findDAGsWithUpstreamDownstream(dagName);
                        matches.forEach(id => results.add(id));
                    } else if (term.startsWith('+')) {
                        // +dag_name - show dag and all its upstream (parents)
                        const dagName = term.slice(1);
                        const matches = findDAGsWithUpstream(dagName);
                        matches.forEach(id => results.add(id));
                    } else if (term.endsWith('+')) {
                        // dag_name+ - show dag and all its downstream (children)
                        const dagName = term.slice(0, -1);
                        const matches = findDAGsWithDownstream(dagName);
                        matches.forEach(id => results.add(id));
                    } else if (term.startsWith('@')) {
                        // @dag_name - exact match only
                        const dagName = term.slice(1);
                        const matches = dagData.nodes.filter(n => n.id === dagName);
                        matches.forEach(n => results.add(n.id));
                    } else {
                        // Regular substring search
                        const matches = dagData.nodes.filter(n => 
                            n.id.toLowerCase().includes(term)
                        );
                        matches.forEach(n => results.add(n.id));
                    }
                }
                
                return results;
            }
            
            function findDAGsWithUpstream(dagName) {
                const results = new Set();
                const queue = [];
                
                // Find matching DAGs
                const startDAGs = dagData.nodes.filter(n => 
                    n.id.toLowerCase().includes(dagName.toLowerCase())
                );
                
                startDAGs.forEach(dag => {
                    results.add(dag.id);
                    queue.push(dag.id);
                });
                
                // Find all upstream DAGs (parents)
                while (queue.length > 0) {
                    const currentDAG = queue.shift();
                    dagData.links.forEach(link => {
                        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                        if (targetId === currentDAG && !results.has(sourceId)) {
                            results.add(sourceId);
                            queue.push(sourceId);
                        }
                    });
                }
                
                return results;
            }
            
            function findDAGsWithDownstream(dagName) {
                const results = new Set();
                const queue = [];
                
                // Find matching DAGs
                const startDAGs = dagData.nodes.filter(n => 
                    n.id.toLowerCase().includes(dagName.toLowerCase())
                );
                
                startDAGs.forEach(dag => {
                    results.add(dag.id);
                    queue.push(dag.id);
                });
                
                // Find all downstream DAGs (children)
                while (queue.length > 0) {
                    const currentDAG = queue.shift();
                    dagData.links.forEach(link => {
                        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                        if (sourceId === currentDAG && !results.has(targetId)) {
                            results.add(targetId);
                            queue.push(targetId);
                        }
                    });
                }
                
                return results;
            }
            
            function findDAGsWithUpstreamLevels(dagName, levels) {
                const results = new Set();
                let currentLevel = [];
                
                // Find matching DAGs
                const startDAGs = dagData.nodes.filter(n => 
                    n.id.toLowerCase().includes(dagName.toLowerCase())
                );
                
                startDAGs.forEach(dag => {
                    results.add(dag.id);
                    currentLevel.push(dag.id);
                });
                
                // Find upstream DAGs level by level
                for (let level = 0; level < levels; level++) {
                    const nextLevel = [];
                    currentLevel.forEach(currentDAG => {
                        dagData.links.forEach(link => {
                            const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                            const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                            if (targetId === currentDAG && !results.has(sourceId)) {
                                results.add(sourceId);
                                nextLevel.push(sourceId);
                            }
                        });
                    });
                    currentLevel = nextLevel;
                    if (currentLevel.length === 0) break;
                }
                
                return results;
            }
            
            function findDAGsWithDownstreamLevels(dagName, levels) {
                const results = new Set();
                let currentLevel = [];
                
                // Find matching DAGs
                const startDAGs = dagData.nodes.filter(n => 
                    n.id.toLowerCase().includes(dagName.toLowerCase())
                );
                
                startDAGs.forEach(dag => {
                    results.add(dag.id);
                    currentLevel.push(dag.id);
                });
                
                // Find downstream DAGs level by level
                for (let level = 0; level < levels; level++) {
                    const nextLevel = [];
                    currentLevel.forEach(currentDAG => {
                        dagData.links.forEach(link => {
                            const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                            const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                            if (sourceId === currentDAG && !results.has(targetId)) {
                                results.add(targetId);
                                nextLevel.push(targetId);
                            }
                        });
                    });
                    currentLevel = nextLevel;
                    if (currentLevel.length === 0) break;
                }
                
                return results;
            }
            
            function findDAGsWithUpstreamDownstream(dagName) {
                const results = new Set();
                const queue = [];
                
                // Find matching DAGs
                const startDAGs = dagData.nodes.filter(n => 
                    n.id.toLowerCase().includes(dagName.toLowerCase())
                );
                
                startDAGs.forEach(dag => {
                    results.add(dag.id);
                    queue.push({id: dag.id, direction: 'both'});
                });
                
                // Find upstream and downstream
                while (queue.length > 0) {
                    const {id: currentDAG, direction} = queue.shift();
                    
                    dagData.links.forEach(link => {
                        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                        
                        if (direction === 'both' || direction === 'downstream') {
                            if (sourceId === currentDAG && !results.has(targetId)) {
                                results.add(targetId);
                                queue.push({id: targetId, direction: 'downstream'});
                            }
                        }
                        if (direction === 'both' || direction === 'upstream') {
                            if (targetId === currentDAG && !results.has(sourceId)) {
                                results.add(sourceId);
                                queue.push({id: sourceId, direction: 'upstream'});
                            }
                        }
                    });
                }
                
                return results;
            }
            
            function parseRangeQuery(query) {
                const results = new Set();
                const parts = query.split('+');
                
                console.log(`Range query: "${query}" split into:`, parts);
                
                if (parts.length >= 3) {
                    // Handle different formats:
                    // "+dag_name+1" -> ['', 'dag_name', '1'] -> ALL upstream + 1 downstream
                    // "1+dag_name+" -> ['1', 'dag_name', ''] -> 1 upstream + ALL downstream  
                    // "1+dag_name+2" -> ['1', 'dag_name', '2'] -> 1 upstream + 2 downstream
                    
                    let beforeCount = 0;
                    let afterCount = 0;
                    let allUpstream = false;
                    let allDownstream = false;
                    let searchTerm = '';
                    
                    // Parse beforeCount (first part)
                    if (parts[0] === '') {
                        // "+dag_name+N" means ALL upstream
                        allUpstream = true;
                    } else {
                        beforeCount = parseInt(parts[0]) || 0;
                    }
                    
                    // Parse searchTerm (middle part)
                    searchTerm = parts[1].toLowerCase();
                    
                    // Parse afterCount (last part)
                    if (parts[2] === '') {
                        // "N+dag_name+" means ALL downstream
                        allDownstream = true;
                    } else {
                        afterCount = parseInt(parts[2]) || 0;
                    }
                    
                    console.log(`Range query parsed: allUpstream=${allUpstream}, beforeCount=${beforeCount}, searchTerm="${searchTerm}", afterCount=${afterCount}, allDownstream=${allDownstream}`);
                    
                    // Find matching DAGs
                    const matchingDAGs = dagData.nodes.filter(n => 
                        n.id.toLowerCase().includes(searchTerm)
                    );
                    
                    console.log(`Found ${matchingDAGs.length} matching DAGs:`, matchingDAGs.map(d => d.id));
                    
                    matchingDAGs.forEach(dag => {
                        results.add(dag.id);
                        
                        // Add upstream DAGs
                        if (allUpstream) {
                            // Add ALL upstream dependencies
                            const upstreamResults = findDAGsWithUpstream(dag.id);
                            upstreamResults.forEach(id => results.add(id));
                            console.log(`Added ALL upstream for ${dag.id}:`, Array.from(upstreamResults));
                        } else if (beforeCount > 0) {
                            // Add specific number of upstream levels
                            let upstreamQueue = [dag.id];
                            for (let i = 0; i < beforeCount; i++) {
                                const nextUpstream = [];
                                upstreamQueue.forEach(dagId => {
                                    dagData.links.forEach(link => {
                                        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                                        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                                        if (targetId === dagId && !results.has(sourceId)) {
                                            results.add(sourceId);
                                            nextUpstream.push(sourceId);
                                        }
                                    });
                                });
                                upstreamQueue = nextUpstream;
                                if (upstreamQueue.length === 0) break;
                            }
                        }
                        
                        // Add downstream DAGs
                        if (allDownstream) {
                            // Add ALL downstream dependencies
                            const downstreamResults = findDAGsWithDownstream(dag.id);
                            downstreamResults.forEach(id => results.add(id));
                            console.log(`Added ALL downstream for ${dag.id}:`, Array.from(downstreamResults));
                        } else if (afterCount > 0) {
                            // Add specific number of downstream levels
                            let downstreamQueue = [dag.id];
                            for (let i = 0; i < afterCount; i++) {
                                const nextDownstream = [];
                                downstreamQueue.forEach(dagId => {
                                    dagData.links.forEach(link => {
                                        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
                                        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
                                        if (sourceId === dagId && !results.has(targetId)) {
                                            results.add(targetId);
                                            nextDownstream.push(targetId);
                                        }
                                    });
                                });
                                downstreamQueue = nextDownstream;
                                if (downstreamQueue.length === 0) break;
                            }
                        }
                    });
                }
                
                console.log(`Range query final results:`, Array.from(results));
                return results;
            }
            
            function applyFilter(matchedDAGs) {
                currentHighlighted = matchedDAGs;
                
                // Update nodes - access via global D3 selection
                d3.select("#graph").selectAll(".node")
                    .classed("filtered", d => !matchedDAGs.has(d.id))
                    .classed("highlighted", d => matchedDAGs.has(d.id));
                
                // Update links
                d3.select("#graph").selectAll(".link")
                    .classed("filtered", d => {
                        const sourceId = typeof d.source === 'string' ? d.source : d.source.id;
                        const targetId = typeof d.target === 'string' ? d.target : d.target.id;
                        return !matchedDAGs.has(sourceId) || !matchedDAGs.has(targetId);
                    });
                
                // Update text
                d3.select("#graph").selectAll(".node-text")
                    .classed("filtered", d => !matchedDAGs.has(d.id));
            }
            
            function clearSearch() {
                document.getElementById('searchInput').value = '';
                currentHighlighted.clear();
                
                // Remove all filter classes
                d3.select("#graph").selectAll(".node")
                    .classed("filtered", false)
                    .classed("highlighted", false);
                
                d3.select("#graph").selectAll(".link")
                    .classed("filtered", false);
                
                d3.select("#graph").selectAll(".node-text")
                    .classed("filtered", false);
            }
            
            // Load DAG data when page loads
            document.addEventListener('DOMContentLoaded', function() {
                loadDAGData();
            });
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/api/status")
async def status():
    """Simple API endpoint"""
    return {"message": "DAG Dependencies Plugin is running!", "status": "ok"}


@app.get("/api/dag-dependencies")
async def get_dag_dependencies():
    """API endpoint to get real DAG dependencies data using DagBag"""
    try:
        from airflow.models import DagBag
        from airflow.datasets import Dataset
        from airflow.operators.trigger_dagrun import TriggerDagRunOperator
        import inspect
        
        # Load DAGs using DagBag
        dagbag = DagBag(include_examples=False)
        
        if dagbag.import_errors:
            print(f"DAG import errors: {dagbag.import_errors}")
        
        # Process DAGs into nodes
        nodes = []
        for dag_id, dag in dagbag.dags.items():
            # Debug: Print schedule details for any DAG with dataset dependencies
            if dag_id in ["transform_customer_sentiment", "transform_forecast_attendance"]:
                print(f"=== DAG {dag_id} schedule debug ===")
                schedule = getattr(dag, 'schedule', None)
                print(f"Schedule object: {schedule}")
                print(f"Schedule type: {type(schedule)}")
                if hasattr(schedule, 'asset_condition'):
                    print(f"Asset condition: {schedule.asset_condition}")
                print("=== End schedule debug ===")
            
            # Determine DAG type based on schedule (Airflow 3 uses 'schedule' instead of 'schedule_interval')
            dag_type = "manual"
            schedule_str = "None"
            
            # Try both 'schedule' (Airflow 3) and 'schedule_interval' (Airflow 2) for compatibility
            schedule = getattr(dag, 'schedule', None) or getattr(dag, 'schedule_interval', None)
            
            if schedule is not None:
                schedule_type = str(type(schedule))
                
                # Check for cron string schedules
                if isinstance(schedule, str):
                    if "*" in schedule or "/" in schedule or "@" in schedule:
                        dag_type = "scheduled"
                        schedule_str = schedule
                    else:
                        dag_type = "scheduled"
                        schedule_str = str(schedule)
                
                # Check for AssetOrTimeSchedule (blue - has both dataset and time components)
                elif 'AssetOrTimeSchedule' in schedule_type:
                    dag_type = "scheduled"  # Blue color for mixed asset/time schedules
                    if hasattr(schedule, 'summary'):
                        schedule_str = schedule.summary
                    elif hasattr(schedule, 'description'):
                        schedule_str = schedule.description
                    else:
                        schedule_str = "Asset or Time Schedule"
                
                # Check for pure dataset schedules (AssetAny, AssetAll, single Asset)
                elif any(asset_type in schedule_type for asset_type in ['AssetAny', 'AssetAll', 'Asset']):
                    dag_type = "dataset"  # Green color for pure dataset schedules
                    schedule_str = "Dataset dependencies"
                
                # Check for other schedule objects that might have timetable (likely cron-based)
                elif hasattr(schedule, 'timetable') or 'Timetable' in schedule_type:
                    dag_type = "scheduled"  # Blue color for timetable-based schedules
                    if hasattr(schedule, 'summary'):
                        schedule_str = schedule.summary
                    elif hasattr(schedule, 'description'):
                        schedule_str = schedule.description
                    else:
                        schedule_str = "Timetable Schedule"
                
                # Fallback for other schedule types
                else:
                    # Try to determine if it's iterable (likely dataset-related)
                    try:
                        list(schedule)
                        dag_type = "dataset"
                        schedule_str = "Dataset dependencies"
                    except (TypeError, AttributeError):
                        dag_type = "scheduled"
                        schedule_str = str(schedule)
            
            nodes.append({
                "id": dag_id,
                "type": dag_type,
                "schedule": schedule_str,
                "is_paused_upon_creation": getattr(dag, 'is_paused_upon_creation', False),
                "description": getattr(dag, 'description', '') or "",
                "fileloc": getattr(dag, 'fileloc', ''),
                "tags": list(getattr(dag, 'tags', set())),
                "owner": getattr(dag, 'owner', 'airflow'),
                "catchup": getattr(dag, 'catchup', False),
                "max_active_runs": getattr(dag, 'max_active_runs', 1)
            })
        
        # Build dependencies by analyzing DAG schedules and tasks
        links = []
        
        def extract_dataset_dependencies(schedule):
            """Extract dataset names from Airflow 3 Asset schedule objects"""
            dataset_names = set()
            if not schedule:
                return dataset_names
            
            def extract_from_asset_condition(condition, depth=0):
                """Recursively extract asset names from arbitrarily nested asset conditions"""
                if not condition:
                    return set()
                
                indent = "  " * depth
                assets = set()
                condition_type = str(type(condition))
                
                print(f"{indent}Processing condition: {condition_type}")
                
                # Check if this is a single Asset object first
                if hasattr(condition, 'name') and hasattr(condition, 'uri') and hasattr(condition, 'group'):
                    assets.add(condition.name)
                    print(f"{indent}Found Asset: {condition.name}")
                    return assets
                
                # For any compound condition (AssetAny, AssetAll, or any other iterable)
                # Try multiple ways to iterate over sub-conditions
                sub_conditions = []
                
                # Method 1: Try direct iteration
                try:
                    sub_conditions = list(condition)
                    print(f"{indent}Direct iteration found {len(sub_conditions)} sub-conditions")
                except (TypeError, AttributeError):
                    pass
                
                # Method 2: Try common attribute names for sub-conditions
                if not sub_conditions:
                    for attr_name in ['_conditions', 'conditions', '_assets', 'assets', '_operands', 'operands']:
                        if hasattr(condition, attr_name):
                            try:
                                attr_value = getattr(condition, attr_name)
                                if hasattr(attr_value, '__iter__') and not isinstance(attr_value, str):
                                    sub_conditions = list(attr_value)
                                    print(f"{indent}Found sub-conditions via {attr_name}: {len(sub_conditions)}")
                                    break
                            except (TypeError, AttributeError):
                                continue
                
                # Method 3: If still no sub-conditions, try to parse string representation
                if not sub_conditions:
                    condition_str = str(condition)
                    print(f"{indent}Parsing string: {condition_str}")
                    import re
                    # Look for Asset(name='...') patterns in the string
                    asset_matches = re.findall(r'Asset\([^)]*name=["\']([^"\']+)["\']', condition_str)
                    for match in asset_matches:
                        assets.add(match)
                        print(f"{indent}String parsed asset: {match}")
                    return assets
                
                # Recursively process all sub-conditions
                for i, sub_condition in enumerate(sub_conditions):
                    print(f"{indent}Processing sub-condition {i+1}/{len(sub_conditions)}")
                    sub_assets = extract_from_asset_condition(sub_condition, depth + 1)
                    assets.update(sub_assets)
                    print(f"{indent}Sub-condition {i+1} contributed: {sub_assets}")
                
                print(f"{indent}Total assets found at this level: {assets}")
                return assets
            
            # Handle AssetOrTimeSchedule objects
            if hasattr(schedule, 'asset_condition'):
                dataset_names.update(extract_from_asset_condition(schedule.asset_condition))
            
            # Handle direct AssetAny/AssetAll objects
            elif hasattr(schedule, '__class__') and ('AssetAny' in str(schedule.__class__) or 'AssetAll' in str(schedule.__class__)):
                dataset_names.update(extract_from_asset_condition(schedule))
            
            # Handle single Asset objects
            elif hasattr(schedule, 'name') and hasattr(schedule, 'uri'):
                dataset_names.add(schedule.name)
            
            # Fallback: try string parsing for any missed cases
            else:
                schedule_str = str(schedule)
                import re
                # Look for Asset(name='...') or Asset(uri='...') patterns
                asset_pattern = r'Asset\([^)]*(?:name|uri)=["\']([^"\']+)["\'][^)]*\)'
                matches = re.findall(asset_pattern, schedule_str)
                for match in matches:
                    dataset_names.add(match)
            
            return dataset_names
        
        # First pass: collect all dataset producers (DAGs that output datasets via task outlets)
        dataset_producers = {}  # dataset_name -> producing_dag_id
        
        for dag_id, dag in dagbag.dags.items():
            # Go through ALL tasks in the DAG to find outlets
            for task in dag.tasks:
                if hasattr(task, 'outlets') and task.outlets:
                    for outlet in task.outlets:
                        # Handle Asset objects and other formats
                        dataset_name = None
                        if hasattr(outlet, 'name'):
                            dataset_name = outlet.name
                        elif hasattr(outlet, 'uri'):
                            dataset_name = outlet.uri
                        elif hasattr(outlet, '_name'):
                            dataset_name = outlet._name
                        elif isinstance(outlet, str):
                            dataset_name = outlet
                        else:
                            # Try to extract from string representation
                            outlet_str = str(outlet)
                            import re
                            # Look for Asset(name='...') patterns first, then Dataset patterns
                            match = re.search(r'Asset\([^)]*name=["\']([^"\']+)["\']', outlet_str)
                            if not match:
                                match = re.search(r'Dataset\(["\']([^"\']+)["\']\)', outlet_str)
                            if match:
                                dataset_name = match.group(1)
                        
                        if dataset_name:
                            dataset_producers[dataset_name] = dag_id
                            print(f"Found dataset producer: {dag_id} produces '{dataset_name}' via task {task.task_id}")
        
        print(f"All dataset producers: {dataset_producers}")
        
        # Second pass: find dataset consumers (DAGs scheduled by datasets) and create links
        for dag_id, dag in dagbag.dags.items():
            # Check for dataset dependencies in schedule
            schedule = getattr(dag, 'schedule', None) or getattr(dag, 'schedule_interval', None)
            if schedule:
                dependent_datasets = extract_dataset_dependencies(schedule)
                if dependent_datasets:
                    print(f"DAG {dag_id} depends on datasets: {dependent_datasets}")
                
                for dataset_name in dependent_datasets:
                    if dataset_name in dataset_producers:
                        producer_dag = dataset_producers[dataset_name]
                        if producer_dag != dag_id:  # Don't link to self
                            links.append({
                                "source": producer_dag,
                                "target": dag_id,
                                "type": "dataset",
                                "dataset": dataset_name
                            })
                            print(f"Created dataset link: {producer_dag} -> {dag_id} (via dataset '{dataset_name}')")
                    else:
                        print(f"Warning: DAG {dag_id} depends on dataset '{dataset_name}' but no producer found")
            
            # Check ALL tasks for TriggerDagRunOperator (scan every task in the DAG)
            for task in dag.tasks:
                # Check if task is a TriggerDagRunOperator
                if hasattr(task, 'trigger_dag_id'):
                    target_dag_id = task.trigger_dag_id
                    if target_dag_id in dagbag.dags:
                        links.append({
                            "source": dag_id,
                            "target": target_dag_id,
                            "type": "trigger",
                            "task_id": task.task_id
                        })
                        print(f"Found trigger: {dag_id}.{task.task_id} triggers {target_dag_id}")
                
                # Also check by class name for broader compatibility
                elif 'TriggerDagRunOperator' in str(type(task)):
                    if hasattr(task, 'trigger_dag_id'):
                        target_dag_id = task.trigger_dag_id
                        if target_dag_id in dagbag.dags:
                            links.append({
                                "source": dag_id,
                                "target": target_dag_id,
                                "type": "trigger",
                                "task_id": task.task_id
                            })
                            print(f"Found trigger (by class): {dag_id}.{task.task_id} triggers {target_dag_id}")
                
                # Debug: Print task info for first few DAGs to understand structure
                if dag_id in ["load_customer_feedback", "transform_sales_aggregator"]:
                    print(f"Task {dag_id}.{task.task_id}: type={type(task)}, attrs={[attr for attr in dir(task) if 'trigger' in attr.lower()]}")
        
        return {
            "nodes": nodes,
            "links": links,
            "source": "dagbag_direct",
            "total_dags": len(nodes),
            "import_errors": len(dagbag.import_errors) if dagbag.import_errors else 0,
            "success": True
        }
        
    except Exception as e:
        print(f"Error using DagBag: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "nodes": [],
            "links": [],
            "source": "error",
            "success": False,
            "error": str(e)
        }


fastapi_app_with_metadata = {
    "app": app,
    "url_prefix": "/dags_dependencies",
    "name": "DAG Dependencies App"
}


dag_dependencies_external_view = {
    "name": "DAG Dependencies",
    "href": "/dags_dependencies/",
    "destination": "nav",
    "category": "browse",
    "url_route": "dag_dependencies"
}


class DagDependenciesPlugin(AirflowPlugin):
    name = "dags_dependencies_plugin"
    fastapi_apps = [fastapi_app_with_metadata]
    external_views = [dag_dependencies_external_view]