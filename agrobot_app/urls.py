from django.contrib import admin
from django.urls import path
from agrobot_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),         
    path("process_text/", views.process_text, name="process_text"),
    path("predict_disease/", views.predict_disease, name="predict_disease"),
]
