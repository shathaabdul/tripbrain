from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.city_results, name='city_results'),
    path('plan/<str:city_name>/', views.city_plan, name='city_plan'),
    path('download/<str:city_name>/', views.download_plan_pdf, name='download_plan_pdf'),  # ✅ Must be here
]
