from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import SignUpForm, LoginForm, PasswordChangingForm
from .models import User, UserPreferences, FriendRequest, Message, Meal, Exercise

from django.db.models import Q


def authentication_check(request, url, title):
    if request.user.is_authenticated:

        received_friend_requests = FriendRequest.objects.filter(to_user=request.user, has_accepted=0, has_denied=0)
        sent_friend_requests = FriendRequest.objects.filter(from_user=request.user, has_accepted=0, has_denied=0)

        return render(request, "healthwithfriends/" + url, {
            "title": title,
            "h1": title,
            "friend_requests": received_friend_requests,
            "other_users": User.objects.all().exclude(id=request.user.id)
                      .exclude(id__in=[friend.id for friend in request.user.friends.all()])
                      .exclude(id__in=[fr.from_user_id for fr in received_friend_requests])
                      .exclude(id__in=[fr.to_user_id for fr in received_friend_requests])
                      .exclude(id__in=[fr.to_user_id for fr in sent_friend_requests])
        })
    else:
        return redirect('login_page')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('signed in')
    else:
        form = LoginForm(request.POST or None)
        if request.POST and form.is_valid():
            user = authenticate(
                request,
                username=request.POST['username'],
                password=request.POST['password'],
            )
            if user:
                login(request, user)
                request.session['username'] = user.username
                return redirect('signed in')

        return render(request, "healthwithfriends/login_page.html", {
            "title": "Login Page",
            "h1": "Login Page",
            'form': form
        })


def logout_view(request):
    logout(request)
    return redirect('login_page')


def signed_in_view(request):
    return authentication_check(request, 'signed_in.html', 'Welcome, ' + request.user.first_name + "!")


def sign_up_view(request):
    if request.user.is_authenticated:
        return redirect('signed in')
    else:
        form = SignUpForm()
        if request.method == "POST":
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                pref = UserPreferences.objects.create(username=user.username)
                user.preferences = pref
                user.bmi = user.calculate_bmi()
                user.set_password(form.cleaned_data['password'])
                user.save()
                login(request, user)
                request.session['username'] = user.username
                return redirect('signed in')
        return render(request, "healthwithfriends/sign_up.html", {
            "title": "Sign Up Page",
            "h1": "Sign Up Page",
            'form': form,
        })


def admin_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return render(request, "healthwithfriends/admin.html", {
                "title": "View All Users",
                "h1": "View All Users",
            })
    return redirect('signed in')


def view_exercise_log(request):
    if request.user.is_authenticated:
        return render(request, "healthwithfriends/exercise_log.html", {
            "title": str(request.user) + '\'s Exercise Log',
            "h1": str(request.user) + '\'s Exercise Log',
        })
    else:
        return redirect('signed in')


def add_meal_view(request):
    return authentication_check(request, 'add_meal.html', 'Add Meal')


def add_exercise_view(request):
    return authentication_check(request, 'add_exercise.html', 'Add Exercise')


def view_private_profile(request):
    return authentication_check(request, 'private_profile.html', str(request.user) + '\'s Private Profile')


def view_privacy_page(request):
    return authentication_check(request, 'privacy.html', 'Privacy')


def view_public_profile(request, id):
    try:
        user = User.objects.get(id=id)
        return render(request, 'healthwithfriends/public_profile.html', {
            'title': 'Public Profile',
            'h1': user.username + '\'s Public Profile',
            'user': user
        })
    except User.DoesNotExist:
        return HttpResponse("This user does not exist.")


def view_settings(request):
    return authentication_check(request, 'settings.html', 'Settings')


def view_test(request):
    return authentication_check(request, 'test.html', 'Test Page')


def view_food_log(request):
    return authentication_check(request, 'food_log.html', str(request.user) + '\'s Food Log')


def view_friends(request):
    return authentication_check(request, 'friends.html', str(request.user) + '\'s Friends')


def view_messages(request, id):
    if request.user.is_authenticated:
        return render(request, "healthwithfriends/messages.html", {
            "id": id,
            'h1': 'Messages',
            'title': 'Messages',
            "messages": Message.objects.filter(Q(sender=id, recipient=request.user.id) | Q(sender=request.user.id, recipient=id)).order_by('date')
            #Message.objects.get(sender_id=id, recipient=request.user.id)
            # Message.objects.get(sender_id=request.user.id, recipient=id)
        })
    else:
        return redirect('login_page')


def password_success(request):
    return authentication_check(request, 'password_success.html', 'Your password was changed successfully.')


def send_request(request, id):
    from_user = request.user
    to_user = User.objects.get(id=id)
    friend_request = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
    if friend_request is not None:
        friend_request[0].has_denied = 0
    friend_request[0].save()
    return redirect('view friends')


def accept_request(request, id):
    friend_request = FriendRequest.objects.get(id=id)
    friend_request.has_accepted = 1
    user1 = request.user
    user2 = friend_request.from_user
    user1.friends.add(user2)
    user2.friends.add(user1)
    friend_request.save()
    return redirect('view friends')


def reject_request(request, id):
    friend_request = FriendRequest.objects.get(id=id)
    friend_request.has_denied = 1
    friend_request.save()
    return redirect('view friends')


def view_meal_calorific_tracker(request, week, type):
    if request.user.is_authenticated:
        r = datetime.strptime(week + '-1', "%Y-W%W-%w")
        if type == "meal":
            mon = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            mon_total = 0
            for i in range(len(mon)):
                mon_total += mon[i].total_calories

            r += timedelta(days=1)
            tue_total = 0
            tue = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(tue)):
                tue_total += tue[i].total_calories

            r += timedelta(days=1)
            wed_total = 0
            wed = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(wed)):
                wed_total += wed[i].total_calories

            r += timedelta(days=1)
            thu_total = 0
            thu = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(thu)):
                thu_total += thu[i].total_calories

            r += timedelta(days=1)
            fri_total = 0
            fri = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(fri)):
                fri_total += fri[i].total_calories

            r += timedelta(days=1)
            sat_total = 0
            sat = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(sat)):
                sat_total += sat[i].total_calories

            r += timedelta(days=1)
            sun_total = 0
            sun = Meal.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(sun)):
                sun_total += sun[i].total_calories
        else:
            mon = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            mon_total = 0
            for i in range(len(mon)):
                mon_total += mon[i].total_calories

            r += timedelta(days=1)
            tue_total = 0
            tue = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(tue)):
                tue_total += tue[i].total_calories

            r += timedelta(days=1)
            wed_total = 0
            wed = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(wed)):
                wed_total += wed[i].total_calories

            r += timedelta(days=1)
            thu_total = 0
            thu = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(thu)):
                thu_total += thu[i].total_calories

            r += timedelta(days=1)
            fri_total = 0
            fri = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(fri)):
                fri_total += fri[i].total_calories

            r += timedelta(days=1)
            sat_total = 0
            sat = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(sat)):
                sat_total += sat[i].total_calories

            r += timedelta(days=1)
            sun_total = 0
            sun = Exercise.objects.filter(user_id=request.user.id, date__year=r.year, date__month=r.month, date__day=r.day)
            for i in range(len(sun)):
                sun_total += sun[i].total_calories

        return render(request, "healthwithfriends/calorie_tracker.html", {
            "title": "Calorific Tracker",
            "h1": "Week " + week[6:] + " " + week[0:4] + " Calorific Tracker",
            "week": week,
            'mon': mon_total,
            'tue': tue_total,
            'wed': wed_total,
            'thu': thu_total,
            'fri': fri_total,
            'sat': sat_total,
            'sun': sun_total
        })
    else:
        return redirect('login_page')


def view_leaderboard(request):
    return authentication_check(request, 'leaderboard.html', 'Most Calories Burned Leaderboard')


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('password success')
