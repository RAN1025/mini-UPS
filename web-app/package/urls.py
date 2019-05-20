from django.urls import path

from . import views

app_name = 'package'

urlpatterns = [
    path('search/', views.searchView, name='search'),
    path('index/', views.indexView, name='index'),
    path('<int:pk>/edit/',views.editView, name='edit'),
    path('comment/',views.commentView,name='comment'),
    path('addcomment/',views.addcommentView,name='addcomment'),
]