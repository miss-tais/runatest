# Generated by Django 3.1 on 2020-08-18 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='path')),
                ('level', models.PositiveIntegerField(db_index=True, verbose_name='level')),
                ('child_count', models.PositiveIntegerField(default=0, verbose_name='child count')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
    ]
