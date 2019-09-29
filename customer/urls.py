from django.conf.urls import url
# from django.urls import path
from . import views

urlpatterns = [
    url(r'^hello/$',views.hello),
    # path('hello/',views.hello),
    url(r'^insertdata/$',views.insertdata),
    url(r'^handle/$',views.handle),
    url(r'^get_echostr/$',views.get_echosor),
    url(r'^get_token/$',views.get_token),
    url(r'^get_userinfo/$',views.get_userinfo),
    url(r'^select_data/$',views.select_data),
]

