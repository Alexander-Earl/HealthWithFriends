from django.urls import path

from django.conf.urls.static import static
from django.conf import settings

from .views import login_view, signed_in_view, sign_up_view, logout_view, add_meal_view, view_private_profile, \
    view_privacy_page, view_public_profile, view_settings, view_test, view_food_log, view_friends, PasswordsChangeView, \
    password_success, add_exercise_view, admin_view, view_exercise_log, send_request, accept_request, reject_request, view_messages, \
    view_meal_calorific_tracker, view_leaderboard

from .api import user_api, update_user, update_preferences, update_profile_pic, get_food, find_user, users_api, get_exercise, all_users_api

urlpatterns = [
    path('', login_view, name='login_page'),
    path('signedin/', signed_in_view, name='signed in'),
    path('signup/', sign_up_view, name='sign up'),
    path('logout/', logout_view, name='logout'),
    path('addmeal/', add_meal_view, name='add meal'),
    path('add_exercise', add_exercise_view, name='add exercise'),
    path('user/', user_api, name='user api'),
    path('privateprofile/', view_private_profile, name='view private profile'),
    path('privacy/', view_privacy_page, name='privacy'),
    path('public/<int:id>', view_public_profile, name='view public profile'),
    path('settings/', view_settings, name='settings1'),
    path('api/user/<int:id>', update_user, name='update user api'),
    path('preferences/<int:pref_id>', update_preferences, name='update preferences api'),
    path('test', view_test),
    path('foodlog', view_food_log, name='view food log'),
    path('api/updateimage', update_profile_pic, name='update_profile_pic'),
    path('api/getfood', get_food, name='get food'),
    path('api/getexercise', get_exercise, name='get exercise'),
    path('friends', view_friends, name='view friends'),
    path('api/finduser', find_user, name='find user'),
    path('password/', PasswordsChangeView.as_view(template_name='healthwithfriends/change_password.html'), name='settings'),
    path('password_success', password_success, name='password success'),
    path('adminpage', admin_view, name='admin'),
    path('users', users_api, name='users api'),
    path('exerciselog', view_exercise_log, name='exercise log'),
    path('add_friend/<int:id>', send_request, name='add_friend'),
    path('accept/<int:id>', accept_request, name='accept'),
    path('reject/<int:id>', reject_request, name='reject'),
    path('messages/<int:id>', view_messages, name='messages'),
    path('tracker/<str:week>/<str:type>', view_meal_calorific_tracker, name='tracker'),
    path('leaderboard', view_leaderboard, name='leaderboard'),
    path('allusers', all_users_api, name='all users')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
