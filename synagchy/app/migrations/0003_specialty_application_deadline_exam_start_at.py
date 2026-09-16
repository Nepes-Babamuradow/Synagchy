from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_university_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialty',
            name='application_deadline',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Resminama tabşyrygynyň gutarýan wagty'),
        ),
        migrations.AddField(
            model_name='specialty',
            name='exam_start_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Synagyň başlaýan wagty'),
        ),
    ]
