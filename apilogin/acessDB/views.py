from rest_framework import generics
from .models import acessDB
from .serializers import acessDBSerializer, UpdateAcessDBSerializer

class acessDBCreateView(generics.ListCreateAPIView):
    queryset = acessDB.objects.all()
    serializer_class = acessDBSerializer

class acessDBDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = acessDB.objects.all()
    serializer_class = acessDBSerializer

class UpdateAcessDBView(generics.UpdateAPIView):
    queryset = acessDB.objects.all()
    serializer_class = UpdateAcessDBSerializer
    lookup_field = 'id'
