# Generated by Django 2.2 on 2019-04-25 00:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(max_length=200)),
                ('context', models.CharField(max_length=10000)),
            ],
        ),
        migrations.CreateModel(
            name='SearchPackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package_id', models.IntegerField()),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('curr_x', models.IntegerField(blank=True, null=True)),
                ('curr_y', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(default='created', max_length=200)),
                ('items', models.CharField(default='', max_length=200)),
                ('amount', models.IntegerField()),
                ('truck_id', models.IntegerField()),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]