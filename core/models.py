from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

ROLE_CHOICES = (('student','Student'),('teacher','Teacher'))

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    # Whether a teacher account has been approved by an admin (added by migration 0005)
    teacher_approved = models.BooleanField(default=False)
    department = models.CharField(max_length=100, blank=True, null=True)
    # Automatically assigned, unique student identifier (CT<year>ST####)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    bio = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    designation = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return self.user.username

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    # optional attachment: image or document (pdf) supporting posts
    attachment = models.FileField(upload_to='post_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    def __str__(self): return f"Post by {self.author.email}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return f"Comment by {self.author.email}"

class Certificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role':'student'})
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='certificates/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_certs')
    feedback = models.TextField(blank=True)
    def __str__(self): return f"{self.title} - {self.student.email}"


class Department(models.Model):
    """A simple admin-managed department list.

    We keep `User.department` as a CharField for backward compatibility but
    provide a `Department` model so admins can manage allowed department
    names centrally. Forms will source department choices from this model.
    """
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Event(models.Model):
    SCOPE_CHOICES = (('department','Department'),('college','College'))
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='college')
    department = models.CharField(max_length=100, blank=True, null=True)
    # Optional registration URL provided by teachers
    registration_link = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    def __str__(self): return self.title

    @property
    def status(self):
        """Return 'upcoming', 'ongoing', or 'completed' based on dates."""
        now = timezone.now()
        try:
            if self.date_from and now < self.date_from:
                return 'upcoming'
            if self.date_to and now > self.date_to:
                return 'completed'
            # If within window or no end provided yet
            if self.date_from and now >= self.date_from:
                return 'ongoing'
        except Exception:
            pass
        return 'ongoing'

    @property
    def status_color(self):
        """Bootstrap color for status badge."""
        return {
            'upcoming': 'info',
            'ongoing': 'success',
            'completed': 'secondary',
        }.get(self.status, 'secondary')

    @property
    def registration_open(self):
        """Return True when a registration link exists and the event hasn't started yet.

        Registration is considered open if `registration_link` is set and the current
        time is strictly before `date_from` (the event start). After the event starts
        this will return False so templates and views can hide/disable registration.
        """
        if not self.registration_link:
            return False
        now = timezone.now()
        try:
            return self.date_from and now < self.date_from
        except Exception:
            return False

class Marks(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role':'student'})
    subject = models.CharField(max_length=200)
    marks_obtained = models.FloatField()
    total_marks = models.FloatField(default=100)
    created_at = models.DateTimeField(default=timezone.now)
    def percentage(self):
        return (self.marks_obtained / self.total_marks * 100) if self.total_marks else 0.0
    def __str__(self): return f"{self.student.email} - {self.subject}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    def __str__(self): return f"Notif for {self.user.email}"


class News(models.Model):
    """News articles posted by students, teachers, or admins.

    Only the author role is displayed on the frontend (not the name).
    """
    title = models.CharField(max_length=255)
    short_description = models.TextField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_role = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-assign author_role if author is present
        try:
            if self.author:
                if getattr(self.author, 'is_staff', False):
                    self.author_role = 'admin'
                else:
                    # Fallback to the user's role field if present
                    self.author_role = getattr(self.author, 'role', '') or ''
        except Exception:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"News: {self.title} ({self.created_at.date()})"
