import datetime
import math

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserPreferences(models.Model):
    username = models.CharField(max_length=50)
    profile_picture = models.BooleanField(default=True)
    age = models.BooleanField(default=True)
    height = models.BooleanField(default=True)
    weight = models.BooleanField(default=True)
    bmi = models.BooleanField(default=True)
    first_name = models.BooleanField(default=True)
    last_name = models.BooleanField(default=True)
    sex = models.BooleanField(default=True)
    weight_units = models.BooleanField(default=True)
    height_units = models.BooleanField(default=True)
    avg_calorific_intake = models.BooleanField(default=True)
    leaderboard = models.BooleanField(default=True)

    def to_dict(self):
        """Method for converting user preferences into to a dictionary"""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'profile_picture': self.profile_picture,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'sex': self.sex,
            'weight_units': self.weight_units,
            'height_units': self.height_units,
            'avg_calorific_intake': self.avg_calorific_intake,
            'leaderboard': self.leaderboard
        }


class extendedUser(BaseUserManager):
    # required method for BaseUserManager
    def create_user(self, first_name, last_name, username, password, email, city, dob, height, weight, is_staff,
                    is_superuser, is_admin):
        pref = UserPreferences.objects.create(username=username)
        email = self.normalize_email(email)
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            dob=dob,
            city=city,
            height=height,
            weight=weight,
            preferences=pref,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_admin=is_admin,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, first_name, last_name, username, password, email, city, dob, height, weight):
        return self.create_user(first_name, last_name, username, password, email, city, dob, height, weight, True, True,
                                True)


class User(AbstractUser):
    TITLE_CHOICES = [
        ("Male", "Male"),
        ('Female', "Female"),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)
    email = models.EmailField(max_length=250, unique=True)
    dob = models.DateField()
    city = models.CharField(max_length=50)
    height = models.FloatField()
    weight = models.FloatField()
    bmi = models.IntegerField(null=True)
    sex = models.CharField(max_length=15, choices=TITLE_CHOICES, default="")
    preferences = models.OneToOneField(UserPreferences, models.CASCADE, null=True)
    profile_pic = models.ImageField(default='default.jpg', null=True, blank=True)
    friends = models.ManyToManyField('User', blank=True)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = extendedUser()

    USERNAME_FIELD = 'username'

    # # this refers to required fields for creating a superuser
    REQUIRED_FIELDS = ["first_name", "last_name", "city", "email", "dob", "height", "weight"]

    def to_dict(self):
        """Method for converting user attributes to a dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'dob': self.dob,
            'city': self.city,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.calculate_bmi(),
            'pref_id': self.preferences.id,
            'preferences': self.preferences.to_dict(),
            'sex': self.sex,
            'public_profile': reverse('view public profile', kwargs={'id': self.id}),
            'api': reverse('update user api', kwargs={'id': self.id}),
            'update_preferences_api': reverse('update preferences api', kwargs={'pref_id': self.preferences.id}),
            'profile_pic': self.profile_pic.url,
            'daily_intake': self.daily_intake(),
            'daily_burned': self.daily_burned(),
            'imperial_height_ft': self.imperial_height_ft(),
            'imperial_height_in': self.imperial_height_in(),
            'imperial_weight_st': self.imperial_weight_st(),
            'imperial_weight_lbs': self.imperial_weight_lbs(),
            'is_active': self.is_active,
            'friends': [friend.id for friend in self.friends.all()],
            'total_calories_burned': self.total_calories_burned(),
            'date_joined': self.date_joined.date()
        }

    def calculate_bmi(self):
        bmi = int(self.weight) / int(self.height) / int(self.height) * 10000
        return round(bmi, 0)

    def calculate_age(self):
        """
            https://www.geeksforgeeks.org/python-program-to-calculate-age-in-year/
        """
        birthDate = self.dob
        today = datetime.date.today()
        age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
        return age

    def imperial_height_ft(self):
        inches = self.height / 2.54  # Convert the height from cm into inches
        feet = inches / 12  # Convert the inches into feet.
        return math.floor(feet)

    def imperial_height_in(self):
        inches = self.height / 2.54  # Convert the height from cm into inches
        feet = inches / 12  # Convert the inches into feet.
        inc = round(inches - 12 * math.floor(feet))  # Calculate the remaining inches from the feet.
        return inc

    def imperial_weight_st(self):
        return math.floor(self.weight/6.35029318)

    def imperial_weight_lbs(self):
        stone = self.weight/6.35029318
        return round((stone-math.floor(stone))*14)

    def avg_calorific_intake(self):
        meals = Meal.objects.all().filter(user_id=self.id)
        total = 0
        if len(meals) == 0:
            return 0
        for m in meals:
            total += m.total_calories
        return round(total / len(meals), 1)

    def daily_intake(self):
        meals = Meal.objects.all().filter(user_id=self.id).filter(date__year=datetime.date.today().strftime("%Y"),
                                                                  date__month=datetime.date.today().strftime("%m"),
                                                                  date__day=datetime.date.today().strftime("%d"))
        total_intake = 0
        for m in meals:
            total_intake += m.total_calories
        return total_intake

    def daily_burned(self):
        activities = Exercise.objects.all().filter(user_id=self.id).filter(date__year=datetime.date.today().strftime("%Y"),
                                                                  date__month=datetime.date.today().strftime("%m"),
                                                                  date__day=datetime.date.today().strftime("%d"))
        total_calories_burned = 0
        for a in activities:
            total_calories_burned += a.total_calories
        return total_calories_burned

    def recommended_intake(self):
        bmr = (10*self.weight)+(6.25*self.height)-((5*self.calculate_age())+5)
        bmr = round(bmr * 1.2)
        return bmr

    def total_calories_burned(self):
        activities = Exercise.objects.all().filter(user_id=self.id)
        total = 0
        for a in activities:
            total += a.total_calories
        return total


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE)
    has_accepted = models.BooleanField(default=0)
    has_denied = models.BooleanField(default=0)

    def to_dict(self):
        return{
            'from_user': self.from_user,
            'to_user': self.to_user
        }


class Meal(models.Model):
    food_items = models.JSONField()
    total_calories = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'id': self.id,
            'food': self.food_items,
            'date': self.date,
            'total_calories': self.total_calories,
            'user_id': self.user.id
        }


class Exercise(models.Model):
    exercise_type = models.CharField(max_length=40)
    duration_mins = models.IntegerField()
    total_calories = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'id': self.id,
            'exercise_type': self.exercise_type,
            'duration_mins': self.duration_mins,
            'total_calories': self.total_calories,
            'date': self.date,
            'user_id': self.user.id
        }


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.IntegerField()
    body = models.CharField(max_length=4092)
    date = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return{
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'body': self.body,
            'date': self.date
        }

