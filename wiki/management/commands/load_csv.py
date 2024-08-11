from django.core.management.base import BaseCommand
from wiki.models import GraphEdge
import csv


class Command(BaseCommand):
    help = "Load CSV data into GraphEdge model"

    def handle(self, *args, **kwargs):
        batch_size = 1000
        batch = []

        with open("wiki/graph1.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                batch.append(GraphEdge(source=row["From"], target=row["To"]))

                # Insert in batches
                if len(batch) >= batch_size:
                    GraphEdge.objects.bulk_create(batch)
                    batch = []

            # Insert any remaining rows
            if batch:
                GraphEdge.objects.bulk_create(batch)

        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))
