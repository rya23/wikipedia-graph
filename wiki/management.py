import csv
from wiki.models import GraphEdge


def load_data():
    with open("wiki/graph1.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            GraphEdge.objects.create(source=row["From"], target=row["To"])
