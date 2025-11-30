from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, TeacherProfile, Certificate, Notification
import datetime

@receiver(post_save, sender=User)
def create_user_related_profiles(sender, instance: User, created, **kwargs):
    """Ensure a per-role profile exists for new users."""
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'teacher':
            TeacherProfile.objects.create(user=instance)

@receiver(post_save, sender=Certificate)
def cert_uploaded(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.student, content=f'Certificate \"{instance.title}\" uploaded and awaiting verification')

@receiver(post_save, sender=User)
def ensure_profiles_exist_on_update(sender, instance: User, **kwargs):
    """If role changed later, ensure appropriate profile exists."""
    if instance.role == 'student':
        StudentProfile.objects.get_or_create(user=instance)
    elif instance.role == 'teacher':
        TeacherProfile.objects.get_or_create(user=instance)


def generate_student_id():
    year = datetime.datetime.now().year
    prefix = f"CT{year}ST"

    last_user = User.objects.filter(student_id__startswith=prefix).order_by("student_id").last()

    if not last_user:
        return prefix + "0001"

    last_id = int(last_user.student_id[-4:])
    new_id = last_id + 1
    return prefix + str(new_id).zfill(4)


@receiver(post_save, sender=User)
def assign_student_id(sender, instance, created, **kwargs):
    # Assign only once at creation for students
    try:
        if created and getattr(instance, 'role', None) == "student":
            if not instance.student_id:
                instance.student_id = generate_student_id()
                instance.save()
    except Exception:
        # Defensive: do not allow signal errors to break user creation
        pass
