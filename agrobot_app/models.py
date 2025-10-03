from django.db import models

class SymptomEntry(models.Model):
    symptom = models.CharField(max_length=200, unique=True)
    possible_causes = models.TextField(help_text='Comma separated causes')
    treatments = models.TextField(help_text='Use | to separate multiple treatments')
    language = models.CharField(max_length=20, default='en')

    def __str__(self):
        return self.symptom
