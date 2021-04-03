"""filter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls import url

urlpatterns = [
    path('',views.index),
    path('create/',views.create),
    path('create/submit',views.submit),
    path('create/submitted',views.submitted),
    path('apply/',views.apply),
    url(r'^applyFor/(?P<id>\d+)$', views.applyFor, name='edit'),
    path('rank/',views.rank),
    path('upload/',views.upload),
]
