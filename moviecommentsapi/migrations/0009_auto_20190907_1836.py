# Generated by Django 2.2.5 on 2019-09-07 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviecommentsapi', '0008_auto_20190907_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='awards',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='movie',
            name='box_office',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='country',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='dvd',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='genre',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='imdb_id',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='imdb_votes',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='language',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='production',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='rated',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='movie',
            name='released',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='runtime',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='movie',
            name='type',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='rating',
            name='source',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='rating',
            name='value',
            field=models.CharField(max_length=30),
        ),
    ]
