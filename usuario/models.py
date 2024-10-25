# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Collaborations(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey('Projects', models.DO_NOTHING, db_column='project', blank=True, null=True)
    role = models.TextField(blank=True, null=True)
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'collaborations'    


class Notifications(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender= models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    is_read = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifications'


class Projects(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    project_type = ArrayField(models.CharField(max_length=500), blank=True, null=True)
    priority = models.TextField(blank=True, null=True)
    responsible = models.ForeignKey('Users', models.DO_NOTHING, db_column='responsible', blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    type_aplyuni = models.TextField(blank=True, null=True)
    objectives = ArrayField(models.CharField(max_length=500), blank=True, null=True)
    necessary_requirements = ArrayField(models.CharField(max_length=500), blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    accepting_applications = models.BooleanField(blank=True, null=True)
    name_uniuser = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'projects'


class Solicitudes(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    id_user = models.ForeignKey('Users', models.DO_NOTHING, db_column='id_user', blank=True, null=True)
    id_project = models.ForeignKey(Projects, models.DO_NOTHING, db_column='id_project', blank=True, null=True)
    status = models.TextField()
    name_user = models.TextField(blank=True, null=True)
    name_lider = models.TextField(blank=True, null=True)
    name_project = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solicitudes'


class TagAssociations(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey('Tags', models.DO_NOTHING, blank=True, null=True)
    project = models.ForeignKey(Projects, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tag_associations'


class Tags(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    search_date = models.DateTimeField(blank=True, null=True)
    counter = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tags'


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    university = models.TextField(blank=True, null=True)
    career = models.TextField(blank=True, null=True)
    cycle = models.TextField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    photo = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    authuser = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    reset_code = models.IntegerField(blank=True, null=True)
    reset_code_created_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'users'

class Forms(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_end = models.DateTimeField(blank=True, null=True)
    user= models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'forms'