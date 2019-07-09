# Generated by Django 2.2.2 on 2019-07-09 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0004_auto_20190707_1948'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collectionevent',
            options={'verbose_name': 'Sammeltermin', 'verbose_name_plural': 'Sammeltermine'},
        ),
        migrations.AlterModelOptions(
            name='collectioneventmember',
            options={'verbose_name': 'Sammelterminteilnehmer/in', 'verbose_name_plural': 'Sammelterminteilnehmende'},
        ),
        migrations.AlterModelOptions(
            name='collectiongroup',
            options={'verbose_name': 'Ortsgruppe', 'verbose_name_plural': 'Ortsgruppen'},
        ),
        migrations.AlterModelOptions(
            name='collectiongroupmember',
            options={'verbose_name': 'Ortsgruppenmitglied', 'verbose_name_plural': 'Ortsgruppenmitglieder'},
        ),
        migrations.AlterModelOptions(
            name='collectionlocation',
            options={'verbose_name': 'Sammelort', 'verbose_name_plural': 'Sammelorte'},
        ),
        migrations.AlterModelOptions(
            name='collectionresult',
            options={'verbose_name': 'Sammelergebnis', 'verbose_name_plural': 'Sammelergebnisse'},
        ),
        migrations.RenameField(
            model_name='collectioneventmember',
            old_name='group',
            new_name='event',
        ),
        migrations.AddField(
            model_name='collectionevent',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='collection.CollectionGroup'),
        ),
    ]
