from django.contrib import admin
from .models import User, StudentProfile, TeacherProfile, Post, Comment, Certificate, Event, Marks, Notification
from .models import Department
from .models import News
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + ((None, {'fields':('role','department','year')}),)

admin.site.register(User, UserAdmin)
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_department', 'get_year', 'avatar')
    list_filter = ('user__department', 'user__year')
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

    def get_department(self, obj):
        return getattr(obj.user, 'department', '')
    get_department.admin_order_field = 'user__department'
    get_department.short_description = 'Department'

    def get_year(self, obj):
        return getattr(obj.user, 'year', '')
    get_year.admin_order_field = 'user__year'
    get_year.short_description = 'Year'
admin.site.register(TeacherProfile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Certificate)
admin.site.register(Event)
admin.site.register(Department)
@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'marks_obtained', 'total_marks', 'created_at')
    list_filter = ('student__department', 'created_at')
    search_fields = ('student__email', 'student__username', 'subject')
    raw_id_fields = ('student',)

admin.site.register(Notification)
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_role', 'created_at')
    list_filter = ('author_role', 'created_at')
    search_fields = ('title', 'short_description', 'content')
    readonly_fields = ('created_at',)
