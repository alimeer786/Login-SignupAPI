from django.urls import path
from .views import acessDBCreateView, acessDBDetailView,UpdateAcessDBView

urlpatterns = [
    path('acessDB/', acessDBCreateView.as_view(), name='acessDB-list-create'),
    path('acessDB/<int:pk>/', acessDBDetailView.as_view(), name='acessDB-detail'),
    path('acessdb/update/<int:id>/', UpdateAcessDBView.as_view(), name='update_acessdb'),

]
