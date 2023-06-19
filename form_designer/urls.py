from django.urls import path

urlpatterns = [
    path(
        "<slug:object_name>/", "form_designer.views.detail", name="form_designer_detail"
    ),
    path(
        "h/<slug:public_hash>/",
        "form_designer.views.detail_by_hash",
        name="form_designer_detail_by_hash",
    ),
]
