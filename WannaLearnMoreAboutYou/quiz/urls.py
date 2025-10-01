from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("second_page/", views.second_page, name="second_page"),
    path("quiz/", views.quiz, name="quiz"),
    path("quiz/<int:hint_index>/", views.quiz_with_hint, name="quiz_with_hint"),
    path("quiz/<int:hint_index>/<str:error>/", views.quiz_with_hint_error, name="quiz_with_hint_error"),
    path("quiz_post/", views.handle_quiz_post, name="quiz_post"),
    path("previous_question/", views.previous_question, name="previous_question"),
    path("feedback/", views.feedback, name="feedback"),
    path("thank_you/", views.thank_you, name="thank_you"),
    path("thank_you_after_feedback/", views.thank_you_after_feedback, name="thank_you_after_feedback"),
    path("qrcode/", views.qrcode_image, name="qrcode"),
]