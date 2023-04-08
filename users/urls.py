# users/urls.py

from django.urls import path

# Import the "views" module. The "dot" tells Python to import views.py from the same directory as this file.
from . import views

# This variable helps Django distinguish this urls.py from those of other applications in the project.
app_name = 'users'

# This is the list of individual pages that can be requested in this application.
# The "path" function takes three arguments:
#  - A string that Django uses to match the URL. It ignores the "base" part of the URL.
#  - The function to call in views.py.
#  - A name for the URL pattern, so we can refer to it elsewhere.
urlpatterns = [
    path('users/dashboard.html', views.users_dashboard, name='users_dashboard')
]
