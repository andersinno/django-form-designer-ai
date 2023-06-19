from django.http import HttpResponse
from django.utils.encoding import force_str

from form_designer.contrib.exporters import FormLogExporterBase

try:
    import xlwt
except ImportError:  # pragma: no cover
    XLWT_INSTALLED = False
else:  # pragma: no cover
    XLWT_INSTALLED = True


class XlsExporter(FormLogExporterBase):
    @staticmethod
    def export_format():
        return "XLS"

    @staticmethod
    def is_enabled():
        return XLWT_INSTALLED

    def init_writer(self):
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet(force_str(self.model._meta.verbose_name_plural))
        self.rownum = 0

    def init_response(self):
        self.response = HttpResponse(content_type="application/ms-excel")
        self.response["Content-Disposition"] = "attachment; filename=%s.xls" % (
            self.model._meta.verbose_name_plural
        )

    def writerow(self, row):
        for i, f in enumerate(row):
            self.ws.write(self.rownum, i, force_str(f))
        self.rownum += 1

    def close(self):
        self.wb.save(self.response)

    def export(self, request, queryset=None):
        return super().export(request, queryset)
