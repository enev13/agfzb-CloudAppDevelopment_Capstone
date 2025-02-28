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
    cartype = models.CharField(
        max_length=45, choices=TYPE_CHOICES, default=SEDAN)
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
            + str(self.dealerId)
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
class DealerReview(object):

    def __init__(self, review):
        from .restapis import analyze_review_sentiments
        # Dealership
        self.dealership = review['dealership'] if 'dealership' in review else 0
        # Reviewer name
        self.name = review['name'] if 'name' in review else ''
        # Purchase
        self.name = review['purchase'] if 'purchase' in review else False
        # Purchase date
        self.purchase_date = review['purchase_date'] if 'purchase_date' in review else 0
        # Car Make
        self.car_make = review['car_make'] if 'car_make' in review else ''
        # Car Model
        self.car_model = review['car_model'] if 'car_model' in review else ''
        # Car year
        self.car_year = review['car_year'] if 'car_year' in review else 0
        # Id
        self.id = review['id'] if 'id' in review else 0
        # Review
        self.review = review['review'] if 'review' in review else ''
        # Sentiment
        self.sentiment = analyze_review_sentiments(self.review) if self.review else 'neutral'

    def __str__(self):
        return "Dealership {} has receieved a {} review by {}".format(self.dealership, self.sentiment, self.name)
