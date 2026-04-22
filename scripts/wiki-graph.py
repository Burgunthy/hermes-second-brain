#!/usr/bin/env python3
"""
wiki-graph.py - Generate knowledge graph from LLM Wiki markdown files.
Extracts wiki links [[...]] and creates a graph JSON for visualization.

Usage: python3 wiki-graph.py
Output: graphify-out/graph.json, graphify-out/graph.html, graphify-out/stats.json
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        result = {}
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        return result
    return {}


def extract_wiki_links(content):
    """Extract all wiki links [[...]] from markdown content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def scan_wiki(wiki_path):
    """Scan wiki directory and extract all documents and links."""
    wiki_path = Path(wiki_path)
    documents = {}
    links = defaultdict(list)

    for md_file in wiki_path.rglob('*.md'):
        if md_file.name == 'index.md':
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = extract_frontmatter(content)
            wiki_links = extract_wiki_links(content)

            doc_id = md_file.stem
            documents[doc_id] = {
                'id': doc_id,
                'path': str(md_file.relative_to(wiki_path)),
                'title': frontmatter.get('title', doc_id),
                'type': frontmatter.get('type', 'unknown'),
                'sources': frontmatter.get('sources', []),
                'related': frontmatter.get('related', []),
                'created': frontmatter.get('created', ''),
                'updated': frontmatter.get('updated', ''),
            }

            for link in wiki_links:
                link_id = link.split('|')[0].strip()
                links[doc_id].append(link_id)
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}")

    return documents, links


def build_graph(documents, links):
    """Build graph structure from documents and links."""
    nodes = []
    edges = []

    for doc_id, doc in documents.items():
        nodes.append({
            'id': doc_id,
            'label': doc['title'],
            'type': doc['type'],
            'path': doc['path'],
        })

    for source, targets in links.items():
        for target in targets:
            if target in documents:
                edges.append({
                    'source': source,
                    'target': target,
                    'type': 'wiki-link',
                })

    return {'nodes': nodes, 'edges': edges}


def main():
    base_path = Path.home() / 'system' / 'second-brain'
    wiki_path = base_path / 'wiki'
    output_path = base_path / 'graphify-out'
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Scanning wiki: {wiki_path}")
    documents, links = scan_wiki(wiki_path)

    print(f"Found {len(documents)} documents")
    print(f"Found {sum(len(v) for v in links.values())} links")

    graph = build_graph(documents, links)

    graph_file = output_path / 'graph.json'
    graph_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False))
    print(f"Graph written to: {graph_file}")

    stats = {
        'generated': datetime.now().isoformat(),
        'total_nodes': len(graph['nodes']),
        'total_edges': len(graph['edges']),
        'nodes_by_type': defaultdict(int),
    }

    for node in graph['nodes']:
        stats['nodes_by_type'][node['type']] += 1

    stats_file = output_path / 'stats.json'
    stats_file.write_text(json.dumps(dict(stats), indent=2))
    print(f"Stats: {dict(stats['nodes_by_type'])}")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>LLM Wiki Knowledge Graph</title>
    <script src="https://cdn.jsdelivr.net/npm/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #graph {{ width: 100vw; height: 100vh; }}
        .info {{ position: absolute; top: 10px; left: 10px; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
    </style>
</head>
<body>
    <div class="info">
        <h2>LLM Wiki Knowledge Graph</h2>
        <p>Nodes: {len(graph['nodes'])} | Edges: {len(graph['edges'])}</p>
        <p><small>Generated: {stats['generated']}</small></p>
    </div>
    <div id="graph"></div>
    <script>
        const data = {{
            nodes: new vis.DataSet({json.dumps(graph['nodes'])}),
            edges: new vis.DataSet({json.dumps(graph['edges'])})
        }};
        const options = {{
            nodes: {{ shape: 'dot', size: 20, font: {{ size: 14 }}, borderWidth: 2 }},
            edges: {{ width: 2, smooth: {{ type: 'continuous' }}, arrows: {{ to: true }} }},
            physics: {{ stabilization: true, barnesHut: {{ gravitationalConstant: -2000, springConstant: 0.04, springLength: 95 }} }}
        }};
        new vis.Network(document.getElementById('graph'), data, options);
    </script>
</body>
</html>"""

    html_file = output_path / 'graph.html'
    html_file.write_text(html_content)
    print(f"HTML viewer written to: {html_file}")


if __name__ == '__main__':
    main()
