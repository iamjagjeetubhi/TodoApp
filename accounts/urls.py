from django.contrib.auth import views as auth_views
from django.conf.urls import url
from . import views
from .views import TodoListView, FeedListView
urlpatterns = [
    url(r'^list/$', FeedListView.as_view(), name='list'),
    url(r'^edit_post/(?P<id>[-\w.]+)/$', views.edit_post, name="edit_post"),
    url(r'^delete_post/(?P<id>[-\w.]+)/$', views.delete_post, name="delete_post"),
    url(r'^mylist/$', TodoListView.as_view(), name='mylist'),
    url(r'^profile/$', views.view_profile, name='view_profile'),
    url(r'^userpage/$', views.userpage, name='userpage'),
    url(r'^edit_profile/$', views.update_profile, name='update_profile'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', auth_views.login,name='login',
        kwargs={'redirect_authenticated_user': True, 'template_name': 'registration/login.html'}),
    url(r'^logout/$', auth_views.logout, name='logout',
        kwargs={'next_page': 'login'}),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^change_password/$', views.change_password, name='change_password'),
]
