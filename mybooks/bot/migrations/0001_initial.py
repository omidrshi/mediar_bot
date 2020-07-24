# Generated by Django 3.0.8 on 2020-07-22 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=64, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=64, null=True)),
                ('last_name', models.CharField(blank=True, max_length=64, null=True)),
                ('username', models.CharField(blank=True, max_length=64, null=True)),
                ('is_bot', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('active', 'Active'), ('banned', 'Banned')], default='active', max_length=10)),
            ],
        ),
    ]
