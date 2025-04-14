from django.contrib import admin
from django.urls import path, include  # Include is used to include other URLconfs

# Include the URLs from the 'qa' app (you can change 'qa' to your app's name)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('qa.urls')),  # Assuming 'qa' is the name of your app
]