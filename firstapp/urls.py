from django.urls import path
from firstapp import views
from firstapp.views import generate_qr_code_image

def qr_code_image(request, qr_code_data):
    """Serve QR code image based on encoded data."""
    qr_code_data = qr_code_data.replace("_", " ")  # Reverse sanitize if necessary
    return generate_qr_code_image(qr_code_data)




urlpatterns = [
     path('login/',views.process_login,name='login'),
     path('forget_pass/',views.forget_pass,name='forget_pass'),
     path('register/',views.process_registration,name='register'),   
     path('logout_view/',views.logout_view,name='logout_view'),
     path('admin_login/<str:username>/<str:password>/', views.admin_login, name='admin_login'),
     path('admin_logout/', views.admin_logout, name='admin_logout'),

     path('daashboard2/',views.daashboard2,name='daashboard2'),
     path('addbus/',views.addbus,name='addbus'),
     path('bus/<int:bus_id>/update/', views.update_bus, name='update_bus'),
     path('delete_bus/<int:bus_id>',views.delete_bus,name='delete_bus'),
     path('viewbus/',views.viewbus,name='viewbus'),


     #------------------Flight--------------------------------------------------

    path('airports/', views.airport_list, name='airport_list'),
    path('upload-airports/', views.upload_airports, name='upload_airports'),

    path('addAirport/', views.airport_create_or_update, name='airport_create'),
    path('airport/<int:airport_id>/', views.airport_create_or_update, name='airport_update'),
    path('airports/<int:pk>/delete/', views.airport_delete, name='airport_delete'),

     # Flight URLs
     path('flights/', views.flight_list, name='flight_list'),
    path('flight_create/', views.flight_create_or_update, name='flight_create'),
    path('flight/<int:pk>/', views.flight_create_or_update, name='flight_update'),
     path('flights/<int:pk>/delete/', views.flight_delete, name='flight_delete'),

     path('flight-schedule/', views.flight_schedule_list, name='flight_schedule_list'),
     path('flight-schedule/create/', views.flight_schedule_create, name='flight_schedule_create'),
     path('flight-schedule/<int:pk>/edit/', views.flight_schedule_update, name='flight_schedule_update'),
     path('flight-schedule/<int:pk>/delete/', views.flight_schedule_delete, name='flight_schedule_delete'),


     path('flight-booking/', views.flight_booking_list, name='flight_booking_list'),
    path('search_airports/', views.search_airports, name='search_airports'),
    path('search_flights/', views.search_flights, name='search_flights'),
    path('select_flight/<int:schedule_id>', views.select_flight, name='select_flight'),
    path('passenger_create', views.passenger_create, name='passenger_create'),
    path('boarding-pass/', views.boarding_pass_view, name='boarding_pass'),


     path('flight-booking/<int:pk>/', views.flight_booking_detail, name='flight_booking_detail'),
     path('flight-booking/create/', views.flight_booking_create, name='flight_booking_create'),
     path('flight-booking/<int:pk>/edit/', views.flight_booking_update, name='flight_booking_update'),
     path('flight-booking/<int:pk>/delete/', views.flight_booking_delete, name='flight_booking_delete'),

      
    
    path('template1/',views.template1,name='template1'),
    path('template2/',views.template2,name='template2'),
    
    path('upload_csv/',views.upload_csv,name='upload_csv'),

#--------------------- User Panel----------------------------------#


    path('',views.index,name='index'),
    path('Buses/',views.user_Buses,name='user_Buses'),
    path('Bus_booking/<int:route_id>/<int:passenger_id>',views.Bus_booking,name='Bus_booking'),
    path('Bus_bookings_list/',views.Bus_bookings_list,name='Bus_bookings_list'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_Bus_booking'),


    path('manage_movie/', views.manage_movie, name='manage_movie'),
    path('movies/', views.movie_list, name='movie_list'),
    path('all-details/', views.all_details, name='all_details'),

path('delete_theater/<int:theater_id>/', views.delete_theater, name='delete_theater'),
    path('delete_screen/<int:screen_id>/', views.delete_screen, name='delete_screen'),
    path('delete_movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('delete_engagement/<int:engagement_id>/', views.delete_engagement, name='delete_engagement'),
    path('delete_movie_timing/<int:timing_id>/', views.delete_movie_timing, name='delete_movie_timing'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('delete_reservation/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),
    path('add_theater/', views.add_theater, name='add_theater'),
    path('add_screen/', views.add_screen, name='add_screen'),
    path('add_movie/', views.add_movie, name='add_movie'),
    path('add_engagement/', views.add_engagement, name='add_engagement'),
    path('add_movie_timing/', views.add_movie_timing, name='add_movie_timing'),
    path('add_movie_category/', views.add_movie_category, name='add_movie_category'),
    path('select_movie/', views.select_movie, name='select_movie'),
    path('select_theater/<int:movie_id>/', views.select_theater, name='select_theater'),
    path('get-reserved-seats/', views.get_reserved_seats, name='get_reserved_seats'),
    path('confirm_reservation/<int:movie_id>/<int:theater_id>/<int:time_id>/', views.confirm_reservation, name='confirm_reservation'),
    path('myMovies/', views.myMovies, name='myMovies'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('qr_code/<str:qr_code_data>/', qr_code_image, name='qr_code_image'),
    path('download_movies_csv/', views.download_movies_csv, name='download_movies_csv'),



    path('seat-chart/', views.reserve_seats, name='seat_chart'),
]
