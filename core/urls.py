from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('cert/upload/', views.upload_certificate, name='upload_certificate'),
    path('cert/<int:pk>/<str:action>/', views.verify_certificate, name='verify_certificate'),
    path('teachers/add-marks/', views.add_marks, name='add_marks'),
    path('teachers/marks/', views.marks_list, name='marks_list'),
    path('teachers/marks/<int:pk>/edit/', views.edit_mark, name='edit_mark'),
    path('teachers/marks/<int:pk>/delete/', views.delete_mark, name='delete_mark'),
    path('teachers/events/', views.events_list, name='events_list'),
    path('teachers/events/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('teachers/events/<int:pk>/delete/', views.delete_event, name='delete_event'),
    path('teachers/students/<int:pk>/toggle-active/', views.toggle_student_active, name='toggle_student_active'),
    path('events/create/', views.create_event, name='create_event'),
    path('notifications/', views.notifications, name='notifications'),
    path('admin/pending-teachers/', views.pending_teachers, name='pending_teachers'),
    path('admin/pending-teachers/<int:pk>/approve/', views.approve_teacher, name='approve_teacher'),
    path('admin/pending-teachers/<int:pk>/reject/', views.reject_teacher, name='reject_teacher'),
    path('profile/<int:pk>/', views.view_profile, name='view_profile'),
    path('college-activity/', views.college_activity, name='college_activity'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('password/change/', views.CustomPasswordChangeView.as_view(template_name='account/password_change.html', success_url='/dashboard/'), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name='password_change_done'),
    # Password reset (forgot password) flows
    path('password/reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('ajax/check-username/', views.check_username, name='check_username'),
    path('ajax/check-email/', views.check_email, name='check_email'),
    path('ajax/comment/<int:pk>/edit/', views.edit_comment, name='ajax_edit_comment'),
    path('ajax/comment/<int:pk>/delete/', views.delete_comment, name='ajax_delete_comment'),
    path('student/<int:pk>/insights/', views.student_insights, name='student_insights'),
    path('events/<int:pk>/registrations/', views.event_registrations, name='event_registrations'),
    path('ajax/notifications/unread/', views.unread_notifications_json, name='ajax_unread_notifications'),
    path('ajax/notifications/mark-read/', views.mark_notification_read, name='ajax_mark_notification_read'),
        path('notifications/clear-read/', views.clear_read_notifications, name='clear_read_notifications'),
    path('ajax/heartbeat/', views.heartbeat, name='ajax_heartbeat'),
    path('bulk-upload-marks/', views.bulk_upload_marks, name='bulk_upload_marks'),
    path('student-availability/', views.student_availability, name='student_availability'),
    path('news/', views.news_list, name='news_list'),
    path('news/add/', views.add_news, name='add_news'),
    path('news/<int:id>/', views.news_detail, name='news_detail'),
    path('news/<int:id>/edit/', views.edit_news, name='edit_news'),
    path('news/<int:id>/delete/', views.delete_news, name='delete_news'),
]
