from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import SymptomEntry

@admin.register(SymptomEntry)
class SymptomEntryAdmin(ImportExportModelAdmin):
    list_display = ('symptom', 'language')
    search_fields = ('symptom', 'possible_causes', 'treatments')
