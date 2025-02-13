from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('manage-posts/', views.manage_posts, name='manage_posts'),
    path('add-post/', views.add_post, name='add_post'),
    path('update-post/<int:pk>/', views.update_post, name='update_post'),
    path('delete-post/<int:pk>/', views.delete_post, name='delete_post'),
    path('author/<int:author_id>/', views.author_posts, name='author_posts'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
     path('author/<int:author_id>/', views.filter_by_author, name='filter_by_author'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)