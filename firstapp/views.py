from django.forms import ValidationError
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.db.models import Q
import qrcode
from io import BytesIO, TextIOWrapper
import csv
from datetime import timedelta,datetime
import json
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from .models import AdminRegistration, Airport, BusBooking, Flight, FlightBooking, FlightSchedule, Location, Movie, Passenger, Screen, Theater, UserRegistration,MovieCategory, MovieTiming,Route,Bus
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render , redirect
from django.core.paginator import Paginator
from .models import Reservation, Engagement
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def admin_login(request, username, password):
    try:
        admin_user = AdminRegistration.objects.get(username=username)

        if password== admin_user.password:
            # Set session variable to indicate login status
            request.session['is_logged_in'] = True
            request.session['admin_first'] = admin_user.firstname
            request.session['admin_last'] = admin_user.lastname
            return redirect('daashboard2')
        else:
            return redirect('/')
    except AdminRegistration.DoesNotExist:
        return redirect('/')
    
def admin_logout(request):
    request.session.flush()  # Clears all session data
    return redirect('/')

def process_registration(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']

        if UserRegistration.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'registration.html')
        
        if UserRegistration.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'registration.html')
        
        UserRegistration(username=username, email=email,lastname=lastname, firstname=firstname,password=make_password(password)).save()

        try:
            subject = "Welcome to Our Platform!"
            html_message = render_to_string('email.html', {'firstname': firstname, 'lastname': lastname})
            plain_message = strip_tags(html_message)
            from_email = 'yashjadav2024@gmail.com'
            to = email
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending email: {e}")
        

        messages.success(request, ' Registration sucessful')
        return redirect('login')
    return render(request, 'registration.html')

def process_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        date_str = request.POST.get('date', '')

        try:
            user = UserRegistration.objects.get(email=email)
            if check_password(password, user.password):
                request.session['email'] = user.email
                messages.success(request, 'Login successful')

                # Debugging: Print or log the next_url value
                print(f"Next URL: {next_url}")
                if date_str:
                    # URL-encode the date string
                    date_encoded = urlencode({'date': date_str})
                    if '?' in next_url:
                        next_url = f"{next_url}&{date_encoded}"
                    else:
                        next_url = f"{next_url}?{date_encoded}"

                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('index')  # Ensure 'index' is the correct URL name
            else:
                messages.error(request, 'Invalid login credentials')
        except UserRegistration.DoesNotExist:
            messages.error(request, 'Invalid login credentials')

    # Handle GET request or failed login
    next_url = request.GET.get('next', '')
    date_str = request.GET.get('date', '')
    return render(request, 'log_2.html', {'next': next_url, 'date': date_str})

def forget_pass(request):
  if request.method == "POST":
    email = request.POST.get('email')
    username = request.POST.get('username')
    passwd = request.POST.get('passwd')
    Cpasswd = request.POST.get('Cpasswd')

    try:
      user = UserRegistration.objects.get(email=email, username=username)
    except UserRegistration.DoesNotExist:
      user = None  # User not found
      messages.error(request, 'Invalid email or username combination.')

    if user and passwd == Cpasswd:
      user.password = make_password(passwd)  # Hash the password
      user.save()  # Update the existing user

      messages.success(request, 'Password reset successful!')
    else:
      messages.error(request, 'Passwords do not match or user not found.')


  return render(request, 'forget_pass.html')

def dashboard(request):
    # Example dashboard view
    if request.session.email:
        return redirect('process_login')  # Redirect to login if not authenticated
    return render(request, 'daashboard2.html')

def logout_view(request):
    request.session.flush()
    messages.success(request,'you have successfully logged out...')
    return redirect('index')



def first_page(request):
    return render(request,'firstpage.html') 

# def login2(request):
#     return render(request,'log_2.html')

def register2(request):
    return render(request,'registration.html')

def daashboard2(request):
    if request.session.get('is_logged_in'):
        return render(request,'daashboard2.html')
    else:
        return redirect('index')


def addbus(request):
    locations = Location.objects.all()

    if request.method == "POST":
        bus_number = request.POST['bus_number']
        capacity = request.POST['capacity']
        start_point = request.POST['start_point']
        end_point = request.POST['end_point']
        timing = request.POST['timing']

        start_point = Location.objects.get(loc_id=start_point)
        end_point = Location.objects.get(loc_id=end_point)

        # Assuming Bus and Route are models that store bus and route information
        bus = Bus.objects.create(bus_number=bus_number, capacity=capacity)
        Route.objects.create(bus=bus,start_point=start_point, end_point=end_point, timing=timing)

        return redirect( 'viewbus')
    return render(request, 'addbus.html', {'locations': locations})

def update_bus(request, bus_id):
    # Fetch the existing bus and route details
    bus = get_object_or_404(Bus, pk=bus_id)
    route = get_object_or_404(Route, bus=bus)
    locations = Location.objects.all()

    if request.method == "POST":
        bus_number = request.POST['bus_number']
        capacity = request.POST['capacity']
        start_point = request.POST['start_point']
        end_point = request.POST['end_point']
        timing = request.POST['timing']

        start_point = Location.objects.get(loc_id=start_point)
        end_point = Location.objects.get(loc_id=end_point)

        # Update the bus and route details
        bus.bus_number = bus_number
        bus.capacity = capacity
        bus.save()

        route.start_point = start_point
        route.end_point = end_point
        route.timing = timing
        route.save()

        return redirect('viewbus')  # Redirect to a list of buses or any other view as required

    context = {
        'bus': bus,
        'route': route,
        'locations': locations
    }
    return render(request, 'update_bus.html', context)

def viewbus(request):
   
    username = request.session.get('username')
    buses =Bus.objects.all()
    routes=Route.objects.all()
    return render(request, 'viewbus.html',{'username' :username, 'buses':buses ,'routes':routes})

def delete_bus(request,bus_id):
    # Route.objects.get(route_id==route_id).delete()
    bus = Bus.objects.get(bus_id=bus_id)
    
    # Delete all routes associated with the bus
    Route.objects.filter(bus=bus).delete()
    
    # Delete the bus
    bus.delete()
    return redirect('viewbus')  

def user_Buses(request):
    email = request.session.get('email')
    user = None
    if email:
        user = UserRegistration.objects.get(email=email)
    buses = Bus.objects.all()
    paginator = Paginator(buses, 9)  # Show 9 buses per page
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)
    return render(request, 'busbook.html', {'user': user,'page_obj': page_obj})

#------------------------------------Movie Booking -----------------------------

def movie_list(request):
    movies = Movie.objects.all()

    # Prepare a list to hold movie data along with engagements
    movie_data = []

    for movie in movies:
        # Get all engagements for the current movie
        engagements = Engagement.objects.filter(movie=movie).select_related('theater', 'screen')

        # Collect data for each engagement
        theater_names = ', '.join(engagement.theater.name for engagement in engagements)
        theater_addresses = ', '.join(engagement.theater.addr for engagement in engagements)
        screen_names = ', '.join(engagement.screen.name if engagement.screen else 'N/A' for engagement in engagements)
        start_dates = ', '.join(engagement.start_date.strftime('%Y-%m-%d') for engagement in engagements)
        end_dates = ', '.join(engagement.end_date.strftime('%Y-%m-%d') for engagement in engagements)

        # Add movie details and engagement details to the list
        movie_data.append({
            'movie': movie,
            'theater_names': theater_names,
            'theater_addresses': theater_addresses,
            'screen_names': screen_names,
            'start_dates': start_dates,
            'end_dates': end_dates,
        })

    return render(request, 'movie_list.html', {'movie_data': movie_data})


def get_reserved_seats(request):
    engagement_id = request.GET.get('engagement_id')
    reservations = Reservation.objects.filter(engagement_id=engagement_id)
    reserved_seats = [reservation.seat_label for reservation in reservations]
    return JsonResponse({'reserved_seats': reserved_seats})

def reserve_seats(request):
    if request.method == 'POST':
        engagement_id = request.POST.get('engagement_id')
        seats = request.POST.get('seats')

        # Convert the JSON string back to a list
        seats_list = json.loads(seats)

        # Ensure engagement exists
        try:
            engagement = Engagement.objects.get(id=engagement_id)
        except Engagement.DoesNotExist:
            return render(request, 'error.html', {'message': 'Engagement not found'})

        reservations = []
        for seat in seats_list:
            reservations.append(Reservation(
                engagement_id=engagement_id,
                seat_label=seat,
                reserved_at=timezone.now(),
                user_id=1  # Uncomment if user management is in place
            ))
        Reservation.objects.bulk_create(reservations)

        return redirect('index')  # Redirect to a success page or another view

    return render(request, 'seat_chart.html', {'message': 'Invalid request method'})

def seat_chart(request):
    return render(request, 'seat_chart.html')
 
def template1(request):
    return render(request,'template1.html')

def template2(request):
    return render(request,'template2.html')

def index(request):
    return render(request,'index.html')

def upload_csv(request):
     return redirect('movie_list')   



#--------------------------------BUS BOOKING----------------------------

def Bus_booking(request,route_id,passenger_id):
    if not request.session.get('email'):
        return redirect('login')
    else:
        email = request.session.get('email')

        if email:
            route_id = route_id
            passenger_id = passenger_id
            
            route = get_object_or_404(Route, pk=route_id)
            passenger = get_object_or_404(UserRegistration, pk=passenger_id)

            BusBooking.objects.create(
                route=route,
                passenger=passenger,
            )
        return redirect('Bus_bookings_list')
        
   
# List BusBookings
def Bus_bookings_list(request):
    if not request.session.get('email'):
        return redirect('login')
    else:
        email = request.session.get('email')

        user= UserRegistration.objects.get(email=email)
        bookings = BusBooking.objects.filter(passenger = user)
    return render(request, 'Bus_booking_list.html', {'bookings': bookings})

def delete_booking(request, booking_id):
    if not request.session.get('email'):
        return redirect('login')
    
    email = request.session.get('email')
    user = UserRegistration.objects.get(email=email)
    
    booking = get_object_or_404(BusBooking, busbooking_id=booking_id, passenger=user)
    booking.delete()
    
    messages.success(request, 'Booking successfully deleted.')
    return redirect('Bus_bookings_list')

#--------------------------------------- Movie Booking  UserSide ---------------
def all_details(request):
    theaters = Theater.objects.all()
    screens = Screen.objects.all()
    movies = Movie.objects.all()
    categories = MovieCategory.objects.all()
    engagements = Engagement.objects.select_related('theater', 'screen', 'movie').all()
    reservations = Reservation.objects.select_related('engagement', 'time', 'user').all()
    timings = MovieTiming.objects.all()

    context = {
        'theaters': theaters,
        'screens': screens,
        'movies': movies,
        'categories': categories,
        'engagements': engagements,
        'reservations': reservations,
        'timings': timings,
    }

    return render(request, 'Movie_details.html', context)

def add_theater(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        addr = request.POST.get('addr')
        theater = Theater(name=name,addr=addr)
        theater.save()
        #return redirect('theater_list')  # Redirect to a list view of theaters or any other desired page
    return redirect('manage_movie')

def add_screen(request):
    if request.method == 'POST':
        theater_id = request.POST.get('theater')
        name = request.POST.get('name')
        theater = Theater.objects.get(id=theater_id)
        screen = Screen(theater=theater, name=name)
        screen.save()
    return redirect('manage_movie')

def add_movie(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')  # Make sure the form has `enctype="multipart/form-data"`
        minutes = request.POST.get('minutes')
        category_id = request.POST.get('cat')
        category = MovieCategory.objects.get(cat_id=category_id)
        movie = Movie(name=name, image=image, minutes=minutes, cat=category)
        movie.save()
        #return redirect('movie_list')  # Redirect to a list view of movies or any other desired page
    return redirect('manage_movie')

def add_engagement(request): 
    if request.method == 'POST':
        theater_id = request.POST.get('theater')
        screen_id = request.POST.get('screen')
        movie_id = request.POST.get('movie')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        theater = Theater.objects.get(id=theater_id)
        screen = Screen.objects.get(id=screen_id)
        movie = Movie.objects.get(id=movie_id)

        engagement = Engagement(theater=theater, screen=screen, movie=movie, start_date=start_date, end_date=end_date)
        engagement.save()
        #return redirect('engagement_list')  # Redirect to a list view of engagements or any other desired page
    return redirect('manage_movie')

def add_movie_timing(request):    
    if request.method == 'POST':
        engagement_id = request.POST.get('engagement')
        timing = request.POST.get('timing')

        engagement = Engagement.objects.get(id=engagement_id)

        movie_timing = MovieTiming(engagement=engagement, timing=timing)
        movie_timing.save()
        #return redirect('movie_timing_list')  # Redirect to a list view of movie timings or any other desired page
    return redirect('manage_movie')

def add_movie_category(request):    
    if request.method == 'POST':
        cat_name = request.POST.get('cat_name')
        movie_category = MovieCategory( cat_name=cat_name)
        movie_category.save()
        #return redirect('movie_timing_list')  # Redirect to a list view of movie timings or any other desired page
    return redirect('manage_movie')

def delete_theater(request, theater_id):
    theater = Theater.objects.get(pk=theater_id)
    theater.delete()
    return redirect('all_details')  # Redirect to your management page

def delete_screen(request, screen_id):
    screen = Screen.objects.get(pk=screen_id)
    screen.delete()
    return redirect('all_details')

def delete_movie(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    movie.delete()
    return redirect('all_details')

def delete_engagement(request, engagement_id):
    engagement = Engagement.objects.get(pk=engagement_id)
    engagement.delete()
    return redirect('all_details')

def delete_movie_timing(request, timing_id):
    timing = MovieTiming.objects.get(pk=timing_id)
    timing.delete()
    return redirect('all_details')

def delete_category(request, category_id):
    category = MovieCategory.objects.get(pk=category_id)
    category.delete()
    return redirect('all_details')

def delete_reservation(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.delete()
    return redirect('all_details')
 
def manage_movie(request):
    theaters = Theater.objects.all()
    categories = MovieCategory.objects.all()
    screens = Screen.objects.all()
    movies = Movie.objects.all()
    engagements = Engagement.objects.all()
    return render(request,'manageMovie.html',{'theaters':theaters,'categories':categories,'screens':screens,'movies':movies,'engagements':engagements})

def select_movie(request):
    movies = Movie.objects.all()
    paginator = Paginator(movies, 9)  # Show 9 buses per page
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)
    return render(request, 'movieBook.html', {'page_obj': page_obj})

def select_theater(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    engagements = Engagement.objects.filter(movie=movie)

    # Get the selected date from the request (if any)
    selected_date = request.GET.get('date')
    
    if selected_date:
        try:
            # Convert the selected date from 'Aug. 31, 2024' format to 'YYYY-MM-DD' format
            selected_date = datetime.strptime(selected_date, '%b. %d, %Y').date()
        except ValueError:
            selected_date = None  # Handle the case where the date is invalid

    # Find the earliest start date and latest end date
    earliest_start_date = min(engagement.start_date for engagement in engagements)
    latest_end_date = max(engagement.end_date for engagement in engagements)
    
    # Generate all dates between the earliest start date and latest end date
    date_list = []
    current_date = earliest_start_date
    while current_date <= latest_end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    # Filter engagements based on the selected date
    if selected_date:
        engagements = engagements.filter(start_date__lte=selected_date, end_date__gte=selected_date)
    
    # Create a dictionary to store theaters and their corresponding timings and dates
    theater_timings = {}
    
    for engagement in engagements:
        timings = MovieTiming.objects.filter(engagement=engagement)

        theater_timings[engagement.theater] = {
            'screen': engagement.screen,
            'timings': list(timings),  # Include timing objects with IDs
        }
    
    return render(request, 'select_theater.html', {
        'movie': movie, 
        'theater_timings': theater_timings,
        'date_list': date_list,  # Pass the full date range to the template
        'selected_date': selected_date  # Pass the selected date to the template
    })

def confirm_reservation(request, movie_id, theater_id, time_id):
    # Retrieve the selected date from the query parameters
    date_str = request.GET.get('date')
    
    # Convert the date string to a date object
    selected_date = datetime.strptime(date_str, '%b. %d, %Y').date() if date_str else None

    movie = get_object_or_404(Movie, pk=movie_id)
    theater = get_object_or_404(Theater, pk=theater_id)
    engagement = get_object_or_404(Engagement, movie=movie, theater=theater)
    time = get_object_or_404(MovieTiming, engagement=engagement, id=time_id)

    if request.method == 'POST':
        user_email = request.session.get('email')
        if not user_email:
            next_url = reverse('confirm_reservation', args=[movie_id, theater_id, time_id])
            query_params = urlencode({'date': date_str})
            login_url = reverse('login')
            full_login_url = f"{login_url}?next={next_url}&{query_params}"
            return redirect(full_login_url)
        
        user = UserRegistration.objects.get(email=user_email)

        if not (engagement.start_date <= selected_date <= engagement.end_date):
            return render(request, 'seat_chart.html', {
                'error': 'Selected date is out of the engagement period.', 
                'movie_id': movie_id, 
                'theater_id': theater_id,
                'time_id': time_id,
                'date_list': [engagement.start_date + timedelta(days=i) for i in range((engagement.end_date - engagement.start_date).days + 1)]
            })

        seats = request.POST.get('seats')
        seats_list = json.loads(seats) if seats else []

        reservations = []
        for seat in seats_list:
            reservations.append(Reservation(
                engagement=engagement,
                date=selected_date,
                time=time,
                seat_label=seat,
                reserved_at=timezone.now(),
                user=user
            ))

        Reservation.objects.bulk_create(reservations)
        return redirect('myMovies')

    reserved_seats = Reservation.objects.filter(
        engagement=engagement,
        date=selected_date,
        time=time
    ).values_list('seat_label', flat=True)

    date_list = [engagement.start_date + timedelta(days=i) for i in range((engagement.end_date - engagement.start_date).days + 1)]

    return render(request, 'seat_chart.html', {
        'movie_id': movie_id,
        'theater_id': theater_id,
        'time_id': time_id,
        'date_list': date_list,
        'reserved_seats': json.dumps(list(reserved_seats)),  # Convert reserved seats to JSON
        'selected_date': selected_date,
    })

def generate_qr_code_image(data):
    """Generate a QR code and return as an image response."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)  # Reset buffer position to the beginning

    return HttpResponse(buffer, content_type="image/png")

def myMovies(request):
    user_email = request.session.get('email')

    if user_email:
        user = UserRegistration.objects.get(email=user_email)
    else:
        return redirect('login')

    reservations = Reservation.objects.filter(user=user).select_related(
        'engagement__theater',
        'engagement__screen',
        'engagement__movie',
        'time'
    )

    grouped_reservations = []

    # Dictionary to track existing grouped reservations
    reservation_dict = {}

    for reservation in reservations:
        key = (reservation.engagement.id, reservation.date, reservation.time.id, reservation.reserved_at)

        qr_code_data = f"{reservation.engagement.theater.name} | Screen: {reservation.engagement.screen.name} | Seats: {reservation.seat_label}"

        if key not in reservation_dict:
            reservation_dict[key] = {
                'engagement': reservation.engagement,
                'date': reservation.date,
                'time': reservation.time,
                'reserved_at': reservation.reserved_at,
                'seats': [reservation.seat_label],
                'total_price': reservation.seat_price,
                'qr_code_data': qr_code_data
            }
        else:
            reservation_dict[key]['seats'].append(reservation.seat_label)
            reservation_dict[key]['total_price'] += reservation.seat_price

    grouped_reservations = list(reservation_dict.values())

    context = {
        'grouped_reservations': grouped_reservations,
    }

    return render(request, 'MyMovies.html', context)


def download_movies_csv(request):
    # Create an HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="movies_details.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
        'Movie Name','Movie Minutes', 'Movie Language', 'Movie Category',
        'Theater Names', 'Theater Addresses', 'Screen Names',
        'Engagement Start Dates', 'Engagement End Dates', 'Movie Timings'
    ])

    # Query all movies
    movies = Movie.objects.all()

    for movie in movies:
        # Get all engagements for the current movie
        engagements = Engagement.objects.filter(movie=movie).select_related('theater', 'screen')
        
        # Collect comma-separated values for each field
        theater_names = ', '.join(engagement.theater.name for engagement in engagements)
        theater_addresses = ', '.join(engagement.theater.addr for engagement in engagements)
        screen_names = ', '.join(engagement.screen.name if engagement.screen else 'N/A' for engagement in engagements)
        start_dates = ', '.join(engagement.start_date.strftime('%Y-%m-%d') for engagement in engagements)
        end_dates = ', '.join(engagement.end_date.strftime('%Y-%m-%d') for engagement in engagements)
        
        # Collect movie timings
        movie_timings = []
        for engagement in engagements:
            timings = MovieTiming.objects.filter(engagement=engagement).values_list('timing', flat=True)
            movie_timings.extend(timings)
        movie_timings_str = ', '.join(movie_timings)

        # Write the movie and its associated details to the CSV file
        writer.writerow([
            movie.name,
            movie.minutes,
            movie.lang,
            movie.cat.cat_name if movie.cat else 'N/A',
            theater_names,
            theater_addresses,
            screen_names,
            start_dates,
            end_dates,
            movie_timings_str
        ])

    return response
#-------------------------- END Movie Booking UserSide ------------------------------------------

#-------------------------- Flight Booking ------------------------------------------------------

# Airport views
def airport_list(request):
    airports = Airport.objects.all()
    return render(request, 'airport_list.html', {'airports': airports})

def upload_airports(request):
    if request.method == 'POST':
        if 'upload_airports' in request.FILES:
            csv_file = request.FILES['upload_airports']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File is not CSV type')
                return redirect('upload_airports')

            # Read and process the CSV file
            csv_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for row in reader:
                _, created = Airport.objects.update_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['name'],
                        'city': row['city'],
                        'country': row['country']
                    }
                )

            messages.success(request, 'CSV file has been uploaded and processed.')
            return redirect('airport_list')
        else:
            messages.error(request, 'No file selected')
            return redirect('airport_list')

    return redirect('airport_list')

def airport_create_or_update(request, airport_id=None):
    if request.method == "POST":
        name = request.POST.get('name')
        code = request.POST.get('code')
        city = request.POST.get('city')
        country = request.POST.get('country')

        if airport_id:
            # Update existing airport
            airport = get_object_or_404(Airport, pk=airport_id)
            airport.name = name
            airport.code = code
            airport.city = city
            airport.country = country
            airport.save()
        else:
            # Create new airport
            Airport.objects.create(name=name, code=code, city=city, country=country)

        return redirect('airport_list')
    
    if airport_id:
        airport = get_object_or_404(Airport, pk=airport_id)
    else:
        airport = None

    return render(request, 'airport_form.html', {'airport': airport})

def airport_delete(request, pk):
    airport = get_object_or_404(Airport, pk=pk)
    airport.delete()
    return redirect('airport_list')

# Flight views
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'flight_list.html', {'flights': flights})

def flight_create_or_update(request, pk=None):
    if pk:
        # If pk is provided, update an existing flight
        flight = get_object_or_404(Flight, pk=pk)
    else:
        # Otherwise, create a new flight
        flight = None

    if request.method == "POST":
        flight_number = request.POST.get('flight_number')
        airline = request.POST.get('airline')
        capacity = request.POST.get('capacity')

        if flight:
            # Update existing flight
            flight.flight_number = flight_number
            flight.airline = airline
            flight.capacity = capacity
            flight.save()
        else:
            # Create new flight
            Flight.objects.create(flight_number=flight_number, airline=airline, capacity=capacity)

        return redirect('flight_list')

    return render(request, 'flight_form.html', {'flight': flight})

def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    flight.delete()
    return redirect('flight_list')

# FlightSchedule views
def search_airports(request):
    query = request.GET.get('q', '')
    if query:
        airports = Airport.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(city__icontains=query)
        )
        airports = airports[:10]  # Limit to 10 results
        results = [{'name': airport.name, 'code': airport.code, 'city': airport.city} for airport in airports]
    else:
        results = []

    return JsonResponse(results, safe=False)

def flight_schedule_list(request):
    schedules = FlightSchedule.objects.all()
    return render(request, 'flight_schedule_list.html', {'schedules': schedules})

def flight_schedule_create(request):
    if request.method == "POST":
        flight_id = request.POST.get('flight')
        departure_airport_id = request.POST.get('departure_airport')
        arrival_airport_id = request.POST.get('arrival_airport')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        price = request.POST.get('price')

        flight = get_object_or_404(Flight, pk=flight_id)
        departure_airport = get_object_or_404(Airport, pk=departure_airport_id)
        arrival_airport = get_object_or_404(Airport, pk=arrival_airport_id)

        schedule = FlightSchedule(
            flight=flight,
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=price
        )
        try:
            schedule.clean()
            schedule.save()
        except ValidationError as e:
            return render(request, 'flight_schedule_form.html', {'error': e.message})
        
        return redirect('flight_schedule_list')
    
    flights = Flight.objects.all()
    airports = Airport.objects.all()
    return render(request, 'flight_schedule_form.html', {'flights': flights, 'airports': airports})

def flight_schedule_update(request, pk):
    schedule = get_object_or_404(FlightSchedule, pk=pk)
    if request.method == "POST":
        schedule.flight = get_object_or_404(Flight, pk=request.POST.get('flight'))
        schedule.departure_airport = get_object_or_404(Airport, pk=request.POST.get('departure_airport'))
        schedule.arrival_airport = get_object_or_404(Airport, pk=request.POST.get('arrival_airport'))
        schedule.departure_time = request.POST.get('departure_time')
        schedule.arrival_time = request.POST.get('arrival_time')
        schedule.price = request.POST.get('price')

        try:
            schedule.clean()
            schedule.save()
        except ValidationError as e:
            return render(request, 'flight_schedule_form.html', {'schedule': schedule, 'error': e.message})
        
        return redirect('flight_schedule_list')
    
    flights = Flight.objects.all()
    airports = Airport.objects.all()
    return render(request, 'flight_schedule_form.html', {'schedule': schedule, 'flights': flights, 'airports': airports})

def flight_schedule_delete(request, pk):
    schedule = get_object_or_404(FlightSchedule, pk=pk)
    schedule.delete()
    return redirect('flight_schedule_list')

# Passenger views
def passenger_list(request):
    passengers = Passenger.objects.all()
    return render(request, 'passenger_list.html', {'passengers': passengers})

def passenger_detail(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    return render(request, 'passenger_detail.html', {'passenger': passenger})

def passenger_create(request):
    user_email = request.session.get('email')
    user = UserRegistration.objects.get(email = user_email)

    if request.method == "POST":
        user = user
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        passport_number = request.POST.get('passport_number')
        schedule_id = request.POST.get('schedule_id')  # Get schedule_id from the form


        Passenger.objects.create(user=user,firstname=firstname,lastname=lastname,email=email, phone_number=phone_number, passport_number=passport_number)
        return redirect('select_flight', schedule_id=schedule_id)
    
    return redirect('select_flight', schedule_id=schedule_id)

def passenger_update(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    if request.method == "POST":
        passenger.phone_number = request.POST.get('phone_number')
        passenger.passport_number = request.POST.get('passport_number')
        passenger.save()
        return redirect('passenger_list')
    return render(request, 'passenger_form.html', {'passenger': passenger})

def passenger_delete(request, pk):
    passenger = get_object_or_404(Passenger, pk=pk)
    passenger.delete()
    return redirect('passenger_list')

# FlightBooking views
def search_flights(request):
    if request.method == 'POST':
        from_location = request.POST.get('from', '')
        to_location = request.POST.get('to', '')
        depart_date = request.POST.get('depart', '')

        if not from_location or not to_location or not depart_date:
            return render(request, 'flight_booking_list.html', {'error': 'Missing required parameters'})

        try:
            from_airport = Airport.objects.get(name=from_location)
            to_airport = Airport.objects.get(name=to_location)
        except Airport.DoesNotExist:
            return render(request, 'flight_booking_list.html', {'error': 'Airport not found'})

        schedules = FlightSchedule.objects.filter(
            departure_airport=from_airport,
            arrival_airport=to_airport,
            departure_time__date=depart_date
        ).select_related('flight', 'departure_airport', 'arrival_airport')

        for schedule in schedules:
            duration = schedule.arrival_time - schedule.departure_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            schedule.duration_hours = int(hours)
            schedule.duration_minutes = int(minutes)

        return render(request, 'flight_booking_list.html', {'schedules': schedules})
    

    return render(request, 'flight_booking_list.html', {'error': 'Invalid request method'})

def select_flight(request, schedule_id):
    user_email = request.session.get('email')
    
    if not user_email:
        return redirect('login')  # Redirect to login if no user is logged in

    user = get_object_or_404(UserRegistration, email=user_email)
    schedule = get_object_or_404(FlightSchedule, pk=schedule_id)

    # Retrieve reserved seats for the current flight schedule
    reserved_seats = FlightBooking.objects.filter(schedule=schedule).values_list('seat_number', flat=True)

    # Retrieve all passengers associated with the user
    passengers = Passenger.objects.filter(user=user)

    if request.method == 'POST':
        # Get the list of seats from the POST request
        seats = request.POST.get('seats')
        seats_list = json.loads(seats) if seats else []

        # Get selected passenger IDs from the form
        selected_passenger_ids = json.loads(request.POST.get('passenger_ids', '[]'))
        selected_passengers = list(Passenger.objects.filter(id__in=selected_passenger_ids))

        # Ensure that the number of passengers matches the number of seats
        if len(seats_list) != len(selected_passengers):
            # Handle the error, e.g., by returning an error message or redirecting
            return redirect('error_page')  # Replace 'error_page' with the actual error page or handling method

        # Create and save flight bookings for each seat and passenger
        for seat, passenger in zip(seats_list, selected_passengers):
            FlightBooking.objects.create(
                schedule=schedule,
                passenger=passenger,
                seat_number=seat,
                status='Confirmed'  # or 'confirmed' depending on your logic
            )

        # Redirect to a success page or render a confirmation template
        return redirect('boarding_pass')  # Adjust as necessary

    return render(request, 'BookFlights.html', {
        'schedule': schedule,
        'reserved_seats': json.dumps(list(reserved_seats)),
        'passengers': passengers,  # Pass the queryset of passengers to the template
        'schedule_id':schedule_id
    })

def boarding_pass_view(request):
    user_email = request.session.get('email')
    
    if not user_email:
        return redirect('login')  # Redirect to login if no user is logged in

    user = get_object_or_404(UserRegistration, email=user_email)

    passengers = Passenger.objects.filter(user = user)

    bookings = FlightBooking.objects.filter(passenger__in=passengers).select_related('schedule__flight', 'schedule__departure_airport', 'schedule__arrival_airport').order_by('-booking_id')

    context = {
        'bookings': bookings
    }
    
    return render(request,'MyFlights.html',context)


def flight_booking_list(request):
    bookings = FlightBooking.objects.all()
    return render(request, 'flight_booking_list.html', {'bookings': bookings})

def flight_booking_detail(request, pk):
    booking = get_object_or_404(FlightBooking, pk=pk)
    return render(request, 'flight_booking_detail.html', {'booking': booking})

def flight_booking_create(request):
    if request.method == "POST":
        schedule_id = request.POST.get('schedule')
        passenger_id = request.POST.get('passenger')
        seat_number = request.POST.get('seat_number')
        status = request.POST.get('status')
        schedule = get_object_or_404(FlightSchedule, pk=schedule_id)
        passenger = get_object_or_404(Passenger, pk=passenger_id)

        FlightBooking.objects.create(
            schedule=schedule,
            passenger=passenger,
            seat_number=seat_number,
            status=status

        )
        return redirect('flight_booking_list')
    
    schedules = FlightSchedule.objects.all()
    passengers = Passenger.objects.all()
    return render(request, 'flight_booking_form.html', {'schedules': schedules, 'passengers': passengers})

def flight_booking_update(request, pk):
    booking = get_object_or_404(FlightBooking, pk=pk)
    if request.method == "POST":
        booking.schedule = get_object_or_404(FlightSchedule, pk=request.POST.get('schedule'))
        booking.passenger = get_object_or_404(Passenger, pk=request.POST.get('passenger'))
        booking.seat_number = request.POST.get('seat_number')
        booking.status = request.POST.get('status')
        booking.save()
        return redirect('flight_booking_list')
    
    schedules = FlightSchedule.objects.all()
    passengers = Passenger.objects.all()
    return render(request, 'flight_booking_form.html', {'booking': booking, 'schedules': schedules, 'passengers': passengers})

def flight_booking_delete(request, pk):
    booking = get_object_or_404(FlightBooking, pk=pk)
    booking.delete()
    return redirect('boarding_pass')


def generate_pdf(request):
    movies = Movie.objects.all()

    # Prepare a list to hold movie data along with engagements
    movie_data = []

    for movie in movies:
        # Get all engagements for the current movie
        engagements = Engagement.objects.filter(movie=movie).select_related('theater', 'screen')

        # Collect data for each engagement
        theater_names = ', '.join(engagement.theater.name for engagement in engagements)
        theater_addresses = ', '.join(engagement.theater.addr for engagement in engagements)
        screen_names = ', '.join(engagement.screen.name if engagement.screen else 'N/A' for engagement in engagements)
        start_dates = ', '.join(engagement.start_date.strftime('%Y-%m-%d') for engagement in engagements)
        end_dates = ', '.join(engagement.end_date.strftime('%Y-%m-%d') for engagement in engagements)

        # Add movie details and engagement details to the list
        movie_data.append({
            'movie': movie,
            'theater_names': theater_names,
            'theater_addresses': theater_addresses,
            'screen_names': screen_names,
            'start_dates': start_dates,
            'end_dates': end_dates,
        })

        html_string = render_to_string('generate_pdf.html',{
            'movie': movie,
            'theater_names': theater_names,
            'theater_addresses': theater_addresses,
            'screen_names': screen_names,
            'start_dates': start_dates,
            'end_dates': end_dates,
            'movie_data':movie_data
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename = "Movies_Engagements.pdf"' 

        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating Pdf", status=500)

    return response
    # return render(request, 'generate_pdf.html',{'movie_data':movie_data})
