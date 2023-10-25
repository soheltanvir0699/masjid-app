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
    path('reset-link/', views.requestpasswordresetemail.as_view(), name='request-email'),
    path('compleat/<uidb64>/<token>', views.completepassword, name='compleat'),
    path(r'api/search-masjid/', views.Search_Masjid_View.as_view(), name='search_masjid'),
    path(r'api/all-masjid/', views.All_Masjid_View.as_view(), name='all_masjid'),
    path(r'api/fav-masjid/', views.AddToFavView.as_view(), name='addtofav'),
    path(r'api/update-masjid/', views.update_masjid.as_view(), name='update_masjid'),
    path(r'api/remove-fav-salat/', views.RemoveWithSalatToFavView.as_view(), name='removeFavSalatid'),
    path(r'api/remove-masjid/', views.RemoveMasjidView.as_view(), name='removeMasjid'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path(r'api/remove-fav-fav/', views.RemoveWithFavToFavView.as_view(), name='removeFavFav'),
    path(r'api/create-sch-masjid/', views.create_masjid_date_list.as_view(), name='create_masjid'),
    path(r'api/start-sch/', views.startSch.as_view(), name='startSch'),
    path(r'api/update_sch_masjid/', views.update_masjid_date_list.as_view(), name='updateSch'),
    path(r'api/delete_sch_masjid/', views.delete_masjid_date_list.as_view(), name='deleteSch'),
    path(r'api/update_timezone/', views.TimeZone_Times.as_view(), name='timezone'),
    path(r'api/send_push_notifictions/', views.send_push_notification.as_view(), name='send_push_notification'),
]
