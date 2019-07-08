# Generated by Django 2.2.2 on 2019-06-23 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("collection", "0002_auto_20190623_1521"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectionlocation",
            name="end",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="collectionlocation",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="collectionresult",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="collectionlocation",
            name="start",
            field=models.DateField(blank=True, null=True),
        ),
    ]
