// Idea Visualizer — Cytoscape force-directed (Obsidian-style) graph.
(function () {
  let cy;

  const style = [
    { selector: 'node', style: {
        'background-color': 'data(color)',
        'width': 'data(size)', 'height': 'data(size)',
        'label': 'data(label)', 'color': '#e8eef7',
        'font-size': 11, 'text-wrap': 'wrap', 'text-max-width': 120,
        'text-valign': 'center', 'text-halign': 'center',
        'text-outline-color': '#0d1117', 'text-outline-width': 2,
        'border-width': 0,
    }},
    { selector: 'node[level="category"]', style: {
        'font-size': 16, 'font-weight': 'bold', 'text-valign': 'top',
        'text-margin-y': -4, 'border-width': 3, 'border-color': 'data(color)',
        'border-opacity': 0.35,
    }},
    { selector: 'node[level="subcategory"]', style: { 'font-size': 12, 'opacity': 0.95 }},
    { selector: 'node[level="idea"]', style: {
        'background-opacity': 0.85, 'font-size': 10, 'text-valign': 'bottom',
        'text-margin-y': 3,
    }},
    { selector: 'edge', style: {
        'width': 1.5, 'line-color': '#33415c', 'curve-style': 'bezier',
        'target-arrow-shape': 'none', 'opacity': 0.6,
    }},
    { selector: '.faded', style: { 'opacity': 0.12 }},
    { selector: '.highlight', style: { 'opacity': 1, 'line-color': '#7aa2f7' }},
  ];

  async function load() {
    const res = await fetch('/api/graph');
    const data = await res.json();
    const stats = document.getElementById('graph-stats');
    stats.textContent = `${data.stats.entries} ideas · ${data.stats.categories} categories`;

    const elements = [].concat(data.nodes, data.edges);
    if (cy) cy.destroy();
    cy = cytoscape({
      container: document.getElementById('cy'),
      elements, style,
      layout: {
        name: 'fcose', quality: 'proof', animate: true, animationDuration: 600,
        nodeRepulsion: 8000, idealEdgeLength: 90, nestingFactor: 0.1,
        gravity: 0.25, numIter: 2500, randomize: true,
      },
    });

    cy.on('tap', 'node[level="idea"]', (evt) => {
      const id = evt.target.data('entry_id') || evt.target.id();
      if (id) window.location = '/lifecycle/' + id;
    });

    // hover focus
    cy.on('mouseover', 'node', (evt) => {
      const n = evt.target;
      const hood = n.closedNeighborhood().union(n.successors()).union(n.predecessors());
      cy.elements().addClass('faded');
      hood.removeClass('faded').addClass('highlight');
    });
    cy.on('mouseout', 'node', () => {
      cy.elements().removeClass('faded').removeClass('highlight');
    });
  }

  document.getElementById('refresh-graph').addEventListener('click', load);
  load();
})();
