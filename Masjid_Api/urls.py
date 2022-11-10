from django.urls import path

from . import temp_views, views

app_name = 'Api_View'
urlpatterns = [
    path(r'api/login/', views.LoginView.as_view(), name='login'),
    path(r'api/singup/', views.create_auth, name='singup'),
    path(r'api/logout/', views.LogoutView.as_view(), name='logout'),
    path(r'api/salat_times/', views.Salat_Times.as_view(), name='logout'),
    path('', temp_views.index, name='index'),
    path('blog/', temp_views.blog, name='blog'),
    path('about/', temp_views.about, name='about'),
    path('contact/', temp_views.contact, name='contact'),
    path('gallery/', temp_views.gallery, name='gallery'),
    path('download/', temp_views.download, name='download'),
    path(r'api/search-masjid/', views.Search_Masjid_View.as_view(), name='search_masjid'),
    path(r'api/all-masjid/', views.All_Masjid_View.as_view(), name='all_masjid'),
    path(r'api/fav-masjid/', views.AddToFavView.as_view(), name='addtofav'),
    path(r'api/update-masjid/', views.update_masjid.as_view(), name='update_masjid'),
    path(r'api/remove-fav-salat/', views.RemoveWithSalatToFavView.as_view(), name='removeFavSalatid'),
    path(r'api/remove-masjid/', views.RemoveMasjidView.as_view(), name='removeMasjid'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path(r'api/remove-fav-fav/', views.RemoveWithFavToFavView.as_view(), name='removeFavFav'),

]
