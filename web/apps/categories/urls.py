# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from apps.categories import views

urlpatterns = [
    path('categories/', views.CategoriesView.as_view({'post': 'create'})),
    path('categories/<int:pk>/', views.CategoriesView.as_view({'get': 'retrieve'})),
]
