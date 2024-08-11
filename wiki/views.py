from django.shortcuts import render
from django.http import HttpResponse
import networkx as nx
from igraph import Graph as igGraph
import plotly.graph_objects as go
from plotly.offline import plot
from .models import GraphEdge


def home(request):
    if request.method == "POST":
        search = request.POST["search"].title()
        print(search)

        # Query edges that involve the search node
        edges = GraphEdge.objects.filter(source=search) | GraphEdge.objects.filter(
            target=search
        )

        if not edges.exists():
            return render(
                request,
                "wiki/home.html",
                {"message": "No results found for the search term."},
            )

        # Create the graph
        g = igGraph(directed=True)

        # Add vertices and edges
        unique_nodes = set(edges.values_list("source", flat=True)) | set(
            edges.values_list("target", flat=True)
        )
        g.add_vertices(list(unique_nodes))
        g.vs["name"] = list(unique_nodes)

        name_to_index = {name: idx for idx, name in enumerate(g.vs["name"])}

        edge_tuples = [
            (name_to_index[edge.source], name_to_index[edge.target]) for edge in edges
        ]
        g.add_edges(edge_tuples)

        # Compute connected nodes
        connectednodes = g.neighborhood(search, mode="out")
        if len(connectednodes) == 0:
            return render(
                request,
                "wiki/home.html",
                {"message": "No results found for the search term."},
            )

        # Limit the number of nodes to 1000
        if len(connectednodes) > 1000:
            connectednodes = connectednodes[:1000]

        # Induced subgraph for connected nodes
        g = g.induced_subgraph(connectednodes)
        tempgraph = g.to_networkx()
        G = nx.Graph(tempgraph)

        # Compute positions for nodes
        pos = nx.spring_layout(G)
        edge_x, edge_y = [], []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        node_x, node_y = [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=False,
                colorscale="YlGnBu",
                reversescale=True,
                color=[],
                size=[],
                line_width=2,
            ),
        )

        node_adjacencies = [
            len(adjacencies[1]) for node, adjacencies in enumerate(G.adjacency())
        ]
        node_text = [
            f'<a href="https://simple.wikipedia.org/wiki/{g.vs[node]["name"]}">{g.vs[node]["name"]}</a>'
            for node in G.nodes()
        ]

        max_degree = max(node_adjacencies)
        node_trace.marker.color = node_adjacencies
        node_trace.marker.size = [
            10 + 20 * (deg / max_degree) for deg in node_adjacencies
        ]
        node_trace.text = node_text

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=800,
            ),
        )
        plot_div = plot(fig, output_type="div", include_plotlyjs=False)
        return render(request, "wiki/home.html", context={"plot_div": plot_div})

    return render(request, "wiki/home.html")
