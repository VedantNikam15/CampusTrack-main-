"""Add a boolean field `teacher_approved` to the custom User model.

This migration was previously empty (corrupted) and caused a BadMigrationError. Restoring the intended
operation: add a BooleanField defaulting to False.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('core', '0004_user_approval_status'),
	]

	operations = [
		migrations.AddField(
			model_name='user',
			name='teacher_approved',
			field=models.BooleanField(default=False),
		),
	]
