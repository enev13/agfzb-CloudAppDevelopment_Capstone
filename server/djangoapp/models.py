from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(null=False, max_length=64, default="Audi")
    description = models.CharField(null=True, max_length=512)

    def __str__(self):
        return "Car make:" + self.name + " Description:" + self.description


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"
    HATCHBACK = "Hatchback"
    TYPE_CHOICES = [
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "Wagon"),
        (HATCHBACK, "Hatchback"),
    ]
    id = models.IntegerField(primary_key=True, null=False)
    carmake = models.ForeignKey(to=CarMake, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=45, default="A6")
    dealerId = models.IntegerField(null=True)
    cartype = models.CharField(max_length=45, choices=TYPE_CHOICES, default=SEDAN)
    year = models.DateField(null=True)

    def __str__(self):
        return (
            "Car model:"
            + self.name
            + " "
            + self.carmake.name
            + " "
            + self.cartype
            + " dealer:"
            + str(self.dealer)
            + " year:"
            + str(self.year)
        )


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    
    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, id):
        from .restapis import analyze_review_sentiments
        # Dealership
        self.dealership = dealership
        # Reviewer name
        self.name = name
        # Purchase
        self.purchase = purchase
        # Purchase date
        self.purchase_date = purchase_date
        # Car Make
        self.car_make = car_make
        # Car Model
        self.car_model = car_model
        # Car year
        self.car_year = car_year
        # Id
        self.id = id
        # Review
        self.review = review
        # Sentiment
        if self.review:
            self.sentiment = analyze_review_sentiments(self.review)

    def __str__(self):
        return "Dealership {} has receieved a {} review by {}".format(self.dealership, self.sentiment, self.name)
