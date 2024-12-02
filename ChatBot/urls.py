from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
from Homepage.views import AskQuestionView, QuestionsView, FixedQuestionsView, UnAnsweredQuestionsView, CounterView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


ask_question_view = AskQuestionView()
questions_view = QuestionsView()
fixed_question_view = FixedQuestionsView()
unanswered_question_view = UnAnsweredQuestionsView()
counter_view = CounterView()


urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Home page (public, no login required)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('ask_questions/', ask_question_view.question_view, name='Ask_question'),
    path('ask_questions/<str:question_id>/', AskQuestionView.as_view(), name='ask_question_detail'),
    path('ask_una/', ask_question_view.una_question, name='ask_una'),

    path('upload/', login_required(questions_view.upload_file_view), name='upload_file'),
    path('questions/', login_required(questions_view.questions), name='questions_view'),
    path('questions/add/', login_required(questions_view.add_question), name='add_question'),
    path('questions/edit/<uuid:id>/', login_required(questions_view.edit_question), name='edit_question'),
    path('questions/delete/<uuid:id>/', login_required(questions_view.delete_question), name='delete_question'),


    path('fixed_questions/', login_required(fixed_question_view.fixed_questions), name='fixed_questions'),
    path('edit_fixed_question/<uuid:id>/', login_required(fixed_question_view.edit_question), name='edit_fixed_question'),
    path('delete_fixed_question/<uuid:id>/', login_required(fixed_question_view.delete_question), name='delete_fixed_question'),


    path('unanswered_questions/', login_required(unanswered_question_view.unanswered_questions), name='unanswered_questions'),
    path('unanswered_questions/add_answer/<uuid:question_id>/', login_required(unanswered_question_view.add_answer_to_question), name='add_answer_to_unanswered_question'),
    path('unanswered_questions/edit/<uuid:question_id>/', login_required(unanswered_question_view.edit_unanswer_question), name='edit_question_to_unanswered_question'),
    path('unanswered_questions/delete/<uuid:question_id>/', login_required(unanswered_question_view.delete_unanswer_question), name='delete_question_to_unanswered_question'),
    path('delete_all_unanswered_questions/', login_required(unanswered_question_view.delete_all_unanswered_questions), name='delete_all_unanswered_questions'),

    path('counter_view/', counter_view.most_asked_questions, name='counter_view')
]

# Error handlers
handler404 = 'Homepage.views.custom_404'
handler500 = 'Homepage.views.custom_500'
handler403 = 'Homepage.views.custom_403'
handler400 = 'Homepage.views.custom_400'
handler405 = 'homepage.views.custom_405'

# Static files (only in development mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
