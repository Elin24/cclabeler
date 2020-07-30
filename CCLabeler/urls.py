"""CCLabeler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.urls import include, re_path
from . import view

urlpatterns = [
    re_path(r'^$', view.login),
    re_path(r'^table$', view.table),
    re_path(r'^label$', view.label),
    re_path(r'^jump$', view.jump),
    re_path(r'^save$', view.save),
    re_path(r'^summary$', view.summary),
]