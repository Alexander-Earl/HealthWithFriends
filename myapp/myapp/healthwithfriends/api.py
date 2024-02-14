import json
import datetime

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import User, UserPreferences, Meal, Exercise, FriendRequest, Message


def user_api(request):
    """
        API entry point for a getting user info
    """
    return JsonResponse({
        'user': [
            user.to_dict()
            for user in User.objects.all() if user.username == request.session['username']
        ]
    })


def users_api(request):
    """
        API entry point for getting all users excluding the signed in user
    """
    return JsonResponse({
        'users': [
            user.to_dict()
            for user in User.objects.all() if user.username != request.session['username']
        ]
    })


def all_users_api(request):
    """
        API entry point for getting all users INCLUDING the signed in user
    """
    return JsonResponse({
        'users': [
            user.to_dict()
            for user in User.objects.all() if user.preferences.leaderboard == True
        ]
    })


def update_preferences(request, pref_id):
    preferences = get_object_or_404(UserPreferences, id=pref_id)

    if request.method == "PUT":
        PUT = json.loads(request.body)
        preferences.profile_picture = PUT['profile_picture']
        preferences.first_name = PUT['first_name']
        preferences.last_name = PUT['last_name']
        preferences.sex = PUT['sex']
        preferences.age = PUT['age']
        preferences.height = PUT['height']
        preferences.weight = PUT['weight']
        preferences.bmi = PUT['bmi']
        preferences.avg_calorific_intake = PUT['avg_calorific_intake']
        preferences.leaderboard = PUT['leaderboard']
        preferences.save()
        return JsonResponse({})

    elif request.method == "PUT_UNITS":
        PUT = json.loads(request.body)
        preferences.height_units = PUT['height_units']
        preferences.weight_units = PUT['weight_units']
        preferences.save()
        return JsonResponse({})

    return HttpResponseBadRequest("Invalid method")


def update_user(request, id):
    """ API for updating or deleting a user. """

    user = get_object_or_404(User, id=id)

    if request.method == "DELETE":
        user.delete()
        return JsonResponse({})

    elif request.method == "PUT":
        PUT = json.loads(request.body)
        user.first_name = PUT['first_name']
        user.last_name = PUT['last_name']
        user.dob = PUT['dob']
        user.city = PUT['city']
        user.sex = PUT['sex']
        user.bmi = user.calculate_bmi()
        if user.preferences.height_units:
            user.height = int(float(PUT['imperial_height_ft'])*30.48+float(PUT['imperial_height_in'])*2.54)
        else:
            user.height = float(PUT['height'])
        if user.preferences.weight_units:
            user.weight = round(float(PUT['imperial_weight_st'])*6.35029318+float(PUT['imperial_weight_lbs'])*0.45359237, 1)
        else:
            user.weight = float(PUT['weight'])
        user.save()
        return JsonResponse(user.to_dict())

    elif request.method == "PUT_STATUS":
        PUT = json.loads(request.body)
        user = get_object_or_404(User, id=int(PUT['id']))
        if PUT['status'] == "disable":
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return JsonResponse({})

    elif request.method == "POST_MEAL":
        POST = json.loads(request.body)

        meal = Meal.objects.create(food_items=POST['food_items'].title(), total_calories=POST['total_calories'], user=user)  # .title() sets the food items to have an upper case letter at the beginning.
        meal.save()
        return JsonResponse({})

    elif request.method == "POST_EXERCISE":
        POST = json.loads(request.body)
        exercise = Exercise.objects.create(exercise_type=POST['exercise_type'], duration_mins=POST['duration_mins'], total_calories=POST['total_calories'], user=user)
        exercise.save()
        return JsonResponse({})

    elif request.method == "POST_MESSAGE":
        POST = json.loads(request.body)
        message = Message.objects.create(recipient=POST['recipient'], sender=request.user, body=POST['body'])
        message.save()
        return JsonResponse({})

    return HttpResponseBadRequest("Invalid method!!")


def update_profile_pic(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user.username)
        user.profile_pic = request.FILES['profile_pic']
        user.save()
        return JsonResponse(user.to_dict())
    return HttpResponseBadRequest("Invalid method")


def get_food(request):
    if request.method == "POST":
        DICT = json.loads(request.body)
        week = DICT['week']
        year = int(week[0:4])
        week = int(week[6:])
        m = []; t = []; w = []
        th = []; fr = []; s = []; su = []
        food = Meal.objects.all().filter(user_id=request.user.id)
        for f in food:
            date = datetime.date(f.date.year, f.date.month, f.date.day)
            if f.date.year == year and date.isocalendar()[1] == week:
                if date.strftime('%A') == "Monday":
                    m.append(f.to_dict())
                elif date.strftime('%A') == "Tuesday":
                    t.append(f.to_dict())
                elif date.strftime('%A') == "Wednesday":
                    w.append(f.to_dict())
                elif date.strftime('%A') == "Thursday":
                    th.append(f.to_dict())
                elif date.strftime('%A') == "Friday":
                    fr.append(f.to_dict())
                elif date.strftime('%A') == "Saturday":
                    s.append(f.to_dict())
                elif date.strftime('%A') == "Sunday":
                    su.append(f.to_dict())
                else:
                    print("ERROR.")
        return JsonResponse({
            "monday": m,
            "tuesday": t,
            "wednesday": w,
            "thursday": th,
            "friday": fr,
            "saturday": s,
            "sunday": su
        })
    return HttpResponseBadRequest("Invalid method")


def get_exercise(request):
    if request.method == "POST":
        DICT = json.loads(request.body)
        week = DICT['week']
        year = int(week[0:4])
        week = int(week[6:])
        m = []; t = []; w = []
        th = []; fr = []; s = []; su = []
        exercise = Exercise.objects.all().filter(user_id=request.user.id)
        for e in exercise:
            date = datetime.date(e.date.year, e.date.month, e.date.day)
            if e.date.year == year and date.isocalendar()[1] == week:
                if date.strftime('%A') == "Monday":
                    m.append(e.to_dict())
                elif date.strftime('%A') == "Tuesday":
                    t.append(e.to_dict())
                elif date.strftime('%A') == "Wednesday":
                    w.append(e.to_dict())
                elif date.strftime('%A') == "Thursday":
                    th.append(e.to_dict())
                elif date.strftime('%A') == "Friday":
                    fr.append(e.to_dict())
                elif date.strftime('%A') == "Saturday":
                    s.append(e.to_dict())
                elif date.strftime('%A') == "Sunday":
                    su.append(e.to_dict())
                else:
                    print("ERROR.")
        return JsonResponse({
            "monday": m,
            "tuesday": t,
            "wednesday": w,
            "thursday": th,
            "friday": fr,
            "saturday": s,
            "sunday": su
            })
    return HttpResponseBadRequest("Invalid method")


def find_user(request):
    if request.method == "PUT":
        PUT = json.loads(request.body)
        username = PUT["username"]
        if username == request.user.username:
            return HttpResponseBadRequest("Cannot search for yourself.")
        user = User.objects.get(username=username)
        return JsonResponse(user.to_dict())