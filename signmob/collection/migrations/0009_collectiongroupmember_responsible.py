# Generated by Django 2.2.2 on 2019-07-22 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0008_collectionlocation_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectiongroupmember',
            name='responsible',
            field=models.BooleanField(default=False),
        ),
    ]
