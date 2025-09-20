from django.contrib import admin
from django.urls import path, include # Make sure to import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add this line to include all URLs from the portal app
    path('', include('portal.urls')), 
]
