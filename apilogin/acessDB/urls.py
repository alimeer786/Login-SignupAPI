# acessDB/urls.py
from django.urls import path
from .views import (
    acessDBCreateView,
    acessDBDetailView,
    UpdateAcessDBView,
    FilterFieldView,
    MultipleProjectsErectionReportView,
    technical_transmittal_form,
    erection_report,
    manpower_report,
    delivery_order_pdf,
    inspection_report,
    dynamic_view
)

urlpatterns = [
    # Dynamic API routing
    path('main_api/<str:api_name>/', dynamic_view, name='dynamic_view'),

    # CRUD operations for acessDB
    path('acessDB/', acessDBCreateView.as_view(), name='acessDB-list-create'),
    path('acessDB/<int:pk>/', acessDBDetailView.as_view(), name='acessDB-detail'),
    path('acessdb/update/<int:id>/', UpdateAcessDBView.as_view(), name='update_acessdb'),
    path('acessDB/filter/<str:field_name>/', FilterFieldView.as_view(), name='filter-field'),

    # Report generation
    path('generate-multiple-projects-report/', MultipleProjectsErectionReportView.as_view(), name='generate_multiple_projects_report'),

    # Specific reports and forms
    path('technical-transmittal/', technical_transmittal_form, name='technical_transmittal_form'),
    path('erection-report/', erection_report, name='erection_report'),
    path('manpower-report/', manpower_report, name='manpower_report'),
    path('delivery-order/<int:do_number>/', delivery_order_pdf, name='delivery_order_pdf'),
    path('inspection-report/', inspection_report, name='inspection_report'),
]
