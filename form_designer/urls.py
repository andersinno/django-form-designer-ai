from django.urls import re_path

urlpatterns = [
    re_path(
        r"^(?P<object_name>[-\w]+)/$",
        "form_designer.views.detail",
        name="form_designer_detail",
    ),
    re_path(
        r"^h/(?P<public_hash>[-\w]+)/$",
        "form_designer.views.detail_by_hash",
        name="form_designer_detail_by_hash",
    ),
]
