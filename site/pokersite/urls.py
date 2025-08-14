"""
URL configuration for pokersite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
#urls.py
from django.contrib import admin
from django.urls import path
from pages.views import (
    home_view,
    room_view,
    submit_action,
    logout_view,
    login_view,
    register_view,
    get_ui_log,
    get_seat_map,
    leave_room,
    get_turn_status,
    get_game_state,
)
from pages.views import get_ui_log


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('room/', room_view, name='room'),
    path('home/', home_view, name='home'),
    path('submit-action/', submit_action, name='submit_action'),
    path("logout/", logout_view, name="logout"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("ui-log/", get_ui_log, name="ui_log"),
    path("seat-map/", get_seat_map, name="get_seat_map"),
    path("leave-room/", leave_room, name="leave_room"),
    path("turn-status/", get_turn_status, name="turn_status"),
    path('get_ui_log/', get_ui_log, name='get_ui_log'),
    path('get_game_state/', get_game_state, name='get_game_state'),


]

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

