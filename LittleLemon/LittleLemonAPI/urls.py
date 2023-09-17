from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = (
[   path('__debug__/', include('debug_toolbar.urls')),
    # path('menu-items', views.MenuItemView.as_view()),
    # path('menu-items/<int:pk>',views.SingleMenuItemView.as_view(), name='menu-item-detail'),
    path('menu-items', views.MenuItemView.as_view({'get': 'list', 'post': 'create','put': 'update', 'patch': 'update', 'delete': 'destroy'})),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view({'get': 'retrieve','post': 'create', 'put': 'update', 'patch': 'update', 'delete': 'destroy'})),
    path('groups/manager/users', views.ManagersView.as_view({'get': 'list', 'post': 'create','put': 'update', 'patch': 'update', 'delete': 'destroy'})),
    path('groups/manager/users/<int:pk>', views.SingleManagersView.as_view({'get': 'retrieve','post': 'create', 'put': 'update', 'patch': 'update', 'delete': 'destroy'})),
    # path('users/', include('djoser.urls')),
    # path('token/login/', include('djoser.urls.authtoken')),
    # path('genre/<int:pk>',views.GenreView.as_view(), name='genre-detail'),
    # path('books-url',views.BookUrlView.as_view(), name='book-url-detail'),
    # path('book-genre-name',views.BookGenreView.as_view(), name='book-url-detail'),
    # path('books_list',views.booklist),
    # path('welcome',views.welcome),
    # path('api-token-auth', obtain_auth_token),
    # path('manager/users', views.manager),
    # path('ratings', views.RatingsView.as_view()),
])