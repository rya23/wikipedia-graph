from django.db import models


class GraphEdge(models.Model):
    source = models.CharField(max_length=255)
    target = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.source} -> {self.target}"
