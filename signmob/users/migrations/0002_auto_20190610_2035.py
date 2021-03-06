# Generated by Django 2.2.2 on 2019-06-10 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(name="user", options={}),
        migrations.AlterModelManagers(name="user", managers=[]),
        migrations.RemoveField(model_name="user", name="first_name"),
        migrations.RemoveField(model_name="user", name="last_name"),
        migrations.AddField(
            model_name="user",
            name="date_deactivated",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="date deactivated"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="date_left",
            field=models.DateTimeField(
                blank=True, default=None, null=True, verbose_name="date left"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="is_deleted",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether this user was deleted.",
                verbose_name="deleted",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                max_length=254,
                null=True,
                unique=True,
                verbose_name="email address",
            ),
        ),
    ]
