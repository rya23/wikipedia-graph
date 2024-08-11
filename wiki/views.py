from django.shortcuts import render
from django.http import HttpResponse
import networkx as nx
import pandas as pd
import random
from igraph import Graph
import igraph as ig
import plotly.graph_objects as go
import networkx as nx
from plotly.offline import plot

# Create your views here.


def home(request):
    if request.method == "POST":
        search = request.POST["search"]
        search = search.title()
        print(search)
        df = pd.read_csv("wiki/graph1.csv")
        print(df.head())
        if (search not in df["From"].values) and (search not in df["To"].values):
            return render(
                request,
                "wiki/home.html",
                {"message": "No results found for the search term."},
            )
        g = ig.Graph(directed=True)

        unique_nodes = pd.unique(df[["From", "To"]].values.ravel("K"))
        g.add_vertices(list(unique_nodes))
        g.vs["name"] = unique_nodes

        name_to_index = {name: idx for idx, name in enumerate(g.vs["name"])}

        edges = [
            (name_to_index[src], name_to_index[dst])
            for src, dst in zip(df["From"], df["To"])
        ]
        print(4)

        g.add_edges(edges)

        connectednodes = g.neighborhood(search, mode="out")
        if len(connectednodes) == 0:
            return render(
                request,
                "wiki/home.html",
                {"message": "No results found for the search term."},
            )

        if len(connectednodes) > 1000:
            connectednodes = connectednodes[:1000]

        g = g.induced_subgraph(connectednodes)

        tempgraph = g.to_networkx()

        G = nx.Graph(tempgraph)

        pos = nx.spring_layout(G)
        edge_x = []
        print(5)

        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = []
        node_y = []
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
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale="YlGnBu",
                reversescale=True,
                color=[],
                size=[],
                line_width=2,
            ),
        )

        node_adjacencies = []
        node_text = []
        for node in G.nodes(data=True):
            node_text.append(
                '<a href="https://simple.wikipedia.org/wiki/'
                + node[1]["name"]
                + '">'
                + node[1]["name"]
                + "</a>"
            )

        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))

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

    else:
        return render(request, "wiki/home.html")
