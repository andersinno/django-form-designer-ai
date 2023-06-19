import csv

from django.http import HttpResponse

from form_designer import settings
from form_designer.contrib.exporters import FormLogExporterBase


class CsvExporter(FormLogExporterBase):
    @staticmethod
    def export_format():
        return "CSV"

    def init_writer(self):
        self.writer = csv.writer(self.response, delimiter=settings.CSV_EXPORT_DELIMITER)

    def init_response(self):
        self.response = HttpResponse(content_type="text/csv")
        self.response[
            "Content-Disposition"
        ] = f"attachment; filename={self.model._meta.verbose_name_plural}.csv"

    def writerow(self, row):
        self.writer.writerow(row)

    def export(self, request, queryset=None):
        return super().export(request, queryset)
