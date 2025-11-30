from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment, Certificate, Marks, Event, StudentProfile, TeacherProfile, Department
from django.forms.widgets import DateTimeInput
from django.core.exceptions import ValidationError
from django.utils import timezone

class UserRegisterForm(UserCreationForm):
    # Add placeholders and classes for better UX; keep ajax-email-check on email
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control ajax-email-check', 'placeholder': 'you@college.edu'}))
    role = forms.ChoiceField(choices=(('student','Student'),('teacher','Teacher')), widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_department'}))
    # Allow the user to type a department when they select 'Other'
    other_department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If Other, enter department name', 'id': 'id_other_department'}))
    year = forms.IntegerField(required=False, label='Education year', widget=forms.NumberInput(attrs={'placeholder': 'Education year (e.g. 3)', 'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Create a password', 'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username','email','role','department','year','password1','password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate department choices from Department model (admin-managed). Keep an empty option.
        try:
            deps = [(d.name, d.name) for d in Department.objects.all()]
        except Exception:
            deps = []
        # Add an explicit 'Other' option so users can type their department
        self.fields['department'].choices = [('', '--- Select department ---')] + deps + [('__other__', 'Other')]

    def clean(self):
        cleaned = super().clean()
        dept = cleaned.get('department')
        other = cleaned.get('other_department')
        # If user selected 'Other', require & use the typed value
        if dept == '__other__':
            if not other or not other.strip():
                raise ValidationError({'other_department': 'Please enter your department name when selecting Other.'})
            cleaned['department'] = other.strip()
        return cleaned

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Share something with your college...', 'rows': 3}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Write a comment...', 'rows': 2}),
        }

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['title','file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': "Certificate title, e.g. Dean's List", 'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        from .models import News
        model = News
        fields = ['title', 'short_description', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'News title'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Short description (will be truncated on list)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Full content of the news'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class MarksForm(forms.ModelForm):
    class StudentModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj: User) -> str:  # type: ignore[override]
            full_name = obj.get_full_name()
            return full_name if full_name else (obj.username or obj.email)

    student = StudentModelChoiceField(
        queryset=User.objects.filter(role='student', is_active=True).order_by('first_name', 'last_name', 'email')
        ,widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Marks
        fields = ['student','subject','marks_obtained','total_marks']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Subject name, e.g. Mathematics', 'class': 'form-control'}),
            'marks_obtained': forms.NumberInput(attrs={'placeholder': 'Marks obtained', 'class': 'form-control', 'step': '0.01'}),
            'total_marks': forms.NumberInput(attrs={'placeholder': 'Total marks (e.g. 100)', 'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned = super().clean()
        marks_obtained = cleaned.get('marks_obtained')
        total_marks = cleaned.get('total_marks')
        # If one of the fields is missing, let required validators handle it
        if marks_obtained is None or total_marks is None:
            return cleaned

        # Basic numeric sanity checks
        try:
            mo = float(marks_obtained)
            tm = float(total_marks)
        except (TypeError, ValueError):
            raise ValidationError('Marks must be numeric')

        if tm <= 0:
            raise ValidationError({'total_marks': 'Total marks must be greater than zero.'})
        if mo < 0:
            raise ValidationError({'marks_obtained': 'Marks obtained cannot be negative.'})
        if mo > tm:
            # Attach to form non-field errors so it's visible at top and associated with the form
            raise ValidationError('Marks obtained cannot exceed total marks.')

        return cleaned

class EventForm(forms.ModelForm):
    date_from = forms.DateTimeField(widget=DateTimeInput(attrs={'type':'datetime-local'}))
    date_to = forms.DateTimeField(widget=DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model = Event
        fields = ['title','description','date_from','date_to','scope','department','registration_link']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Event title', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Short description of the event', 'rows': 3}),
            'scope': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'registration_link': forms.URLInput(attrs={'placeholder': 'Optional registration URL (https://...)', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        # If both datetimes are provided, ensure end is not before start
        if date_from and date_to:
            if date_to < date_from:
                # Attach error to date_to field
                raise ValidationError({'date_to': 'End date must be the same or after start date.'})

        # Disallow start dates before today's date (local timezone)
        if date_from:
            try:
                # Compare by date to avoid timezone-naive/aware issues when only date comparison is needed
                if getattr(date_from, 'date', None) and date_from.date() < timezone.localdate():
                    raise ValidationError({'date_from': 'Start date cannot be before today.'})
            except Exception:
                # If anything unexpected happens during comparison, skip this additional check
                pass
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate department select from Department model
        try:
            deps = [(d.name, d.name) for d in Department.objects.all()]
        except Exception:
            deps = []
        # If no departments exist, leave choices empty so admin can add them
        self.fields['department'].widget.choices = [('', '--- Select department ---')] + deps
        # Add client-side min attributes to help prevent selecting past datetimes
        try:
            now_local = timezone.localtime(timezone.now())
            min_dt = now_local.strftime('%Y-%m-%dT%H:%M')
            if 'date_from' in self.fields:
                self.fields['date_from'].widget.attrs.setdefault('min', min_dt)
            if 'date_to' in self.fields:
                self.fields['date_to'].widget.attrs.setdefault('min', min_dt)
        except Exception:
            pass


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'department', 'year']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@college.edu', 'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control', 'id': 'id_department'}),
            'year': forms.NumberInput(attrs={'placeholder': 'Education year (e.g. 3)', 'class': 'form-control'}),
        }
        labels = {
            'year': 'Education year',
        }

    # Provide an input for 'Other' departments and server-side handling
    other_department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If Other, enter department name', 'id': 'id_other_department'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            deps = [(d.name, d.name) for d in Department.objects.all()]
        except Exception:
            deps = []
        self.fields['department'].choices = [('', '--- Select department ---')] + deps + [('__other__', 'Other')]
        # If editing an existing user, and their stored department value is not
        # among the admin-managed options, show 'Other' and prefill the text input
        try:
            instance = getattr(self, 'instance', None)
            existing = None
            if instance and getattr(instance, 'department', None):
                existing = instance.department
            # Also respect initial data passed into the form
            if not existing and 'initial' in kwargs and kwargs.get('initial'):
                existing = kwargs.get('initial').get('department')
            if existing:
                # If existing value matches one of the choices, set it; else use Other
                choice_values = [c[0] for c in ([('', '--- Select department ---')] + deps)]
                if existing in choice_values:
                    self.initial.setdefault('department', existing)
                else:
                    self.initial.setdefault('department', '__other__')
                    self.initial.setdefault('other_department', existing)
        except Exception:
            # Defensive: if anything goes wrong, leave defaults untouched
            pass

    def clean(self):
        cleaned = super().clean()
        dept = cleaned.get('department')
        other = cleaned.get('other_department')
        if dept == '__other__':
            if not other or not other.strip():
                raise ValidationError({'other_department': 'Please enter your department name when selecting Other.'})
            cleaned['department'] = other.strip()
        return cleaned


class StudentProfileForm(forms.ModelForm):
    # Present skills as a comma-separated list in a textarea
    skills_text = forms.CharField(
        label='Skills', required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g. Python, Data Science, Public Speaking'})
    )

    class Meta:
        model = StudentProfile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Short bio / interests', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize skills_text from instance.skills
        if self.instance and self.instance.pk and isinstance(self.instance.skills, list):
            self.fields['skills_text'].initial = ', '.join(self.instance.skills)

    def clean(self):
        cleaned = super().clean()
        skills_text = cleaned.get('skills_text', '')
        # Convert comma-separated to list, strip blanks
        skills = [s.strip() for s in skills_text.split(',') if s.strip()]
        cleaned['skills'] = skills
        return cleaned


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['designation']
        widgets = {
            'designation': forms.TextInput(attrs={'placeholder': 'e.g. Assistant Professor', 'class': 'form-control'}),
        }
