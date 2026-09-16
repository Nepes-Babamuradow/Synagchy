from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_subject_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialty',
            name='required_documents',
            field=models.TextField(blank=True, default='', verbose_name='Gerekli resminamalar'),
        ),
    ]
