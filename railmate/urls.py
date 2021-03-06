
"""railmate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    re_path(r'^search/$', views.home_search, name='search'),
    re_path(r'^listTrips/$', views.home, name='getTrips'),
    re_path(r'^createTrip/$', views.create_trip, name='createTrip'),
    # path('create/', views.home_create, name="create"),
    # path('create/', views.home_create, name="create"),
    path('<int:user_id>/', views.user_page, name='User Page'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('edit/', views.editAccount, name='edit'),
    path('messages/', views.messages, name='messages'),
    path('logout/', views.logout, name='logout'),
    path('trip_edit/<int:trip_id>/', views.trip_edit, name='trip_edit'),
    path('trip_delete/<int:trip_id>/', views.trip_delete, name='trip_delete'),
    path('add_passenger/<int:trip_id>', views.add_passenger, name='add_passenger'),
    path('remove_passenger/<int:passenger_id>', views.remove_passenger, name='remove_passenger')
]
