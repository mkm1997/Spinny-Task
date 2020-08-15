from django.urls import  re_path
from . import  views

urlpatterns = [
    re_path("addUser/$", views.addUser),
    re_path("login/$", views.loginUser),
    re_path("addBox/$", views.addBox),
    re_path("updateBox/$", views.updateBox),
    re_path("deleteBox/$", views.deleteBox),
    re_path("getAllBoxes/$", views.listBoxApiForAll),
    re_path("getMyBoxes/$", views.getMyBoxList)


]
