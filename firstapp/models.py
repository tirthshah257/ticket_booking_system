from django.db import models
from django.forms import ValidationError

class AdminRegistration(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    firstname = models.CharField(max_length=150, null=True, blank=True)
    lastname = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=True)  # Set to True for admin users

    def __str__(self):
        return self.username

class UserRegistration(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    firstname = models.CharField(max_length=150,null=True)
    lastname = models.CharField(max_length=150,null=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

#----------------------------- Bus Booking ------------------------------------#

class Bus(models.Model):
    bus_id = models.AutoField(primary_key=True)
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.bus_number

class Location(models.Model):
    loc_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100)

    def __str__(self):
        return self.location_name

class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='routes')
    start_point = models.ForeignKey(Location, related_name='route_start', on_delete=models.CASCADE)
    end_point = models.ForeignKey(Location, related_name='route_end', on_delete=models.CASCADE)
    timing = models.CharField(max_length=50,null=True)
    price = models.IntegerField(default=100)
    def __str__(self):
        return f"{self.start_point} to {self.end_point}"

class BusBooking(models.Model):
    busbooking_id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    passenger = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"Booking for {self.passenger.username} on {self.route}"

#----------------------------- Movie Booking ------------------------------------#

class Theater(models.Model):
    name = models.CharField(max_length=50)
    addr = models.CharField(max_length=50,default="N/A Addr")

    def __str__(self):
        return self.name

class Screen(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    #seats = models.IntegerField()

    def __str__(self):
        return f"{self.theater.name} - {self.name if self.name else 'No Name'}"

class MovieCategory(models.Model):
    cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=100)

    def __str__(self):
        return self.cat_name

class Movie(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='movie_Images/',null=True)
    minutes = models.IntegerField()
    lang = models.CharField(max_length=50,default="Hindi")
    cat = models.ForeignKey(MovieCategory, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

class Engagement(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['theater', 'screen', 'movie', 'start_date'], name='unique_engagement')
        ]

    def __str__(self):
        return f"{self.theater.name} - {self.screen.name} - {self.movie.name} ({self.start_date} to {self.end_date})"

class Reservation(models.Model):
    engagement = models.ForeignKey('Engagement', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.ForeignKey('MovieTiming', on_delete=models.CASCADE, null=True,blank=True)
    seat_label = models.CharField(max_length=10)
    seat_price = models.IntegerField(default=100)
    reserved_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserRegistration, on_delete=models.SET_NULL, null=True, blank=True)

class MovieTiming(models.Model):
    engagement = models.ForeignKey('Engagement', on_delete=models.CASCADE, null=True, blank=True)
    timing = models.CharField(max_length=100)

    def __str__(self):
        return self.timing


#----------------------------- Flight Booking ------------------------------------#

class Airport(models.Model):
    airport_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)  # Typically a 3-letter code
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Flight(models.Model):
    flight_id = models.AutoField(primary_key=True)
    flight_number = models.CharField(max_length=10, unique=True)
    airline = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.airline} {self.flight_number}"

class FlightSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    departure_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    arrival_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.flight} from {self.departure_airport} to {self.arrival_airport}"

    def clean(self):
        if self.departure_time >= self.arrival_time:
            raise ValidationError('Departure time must be before arrival time.')

    class Meta:
        indexes = [
            models.Index(fields=['departure_time']),
        ]

class Passenger(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=150,null=True)
    lastname = models.CharField(max_length=150,null=True)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username

class FlightBooking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(FlightSchedule, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ])
    reserved_at = models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return f"Booking for {self.passenger.user.username} on {self.schedule}"