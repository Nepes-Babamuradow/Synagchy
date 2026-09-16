from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_specialty_required_documents'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='exam_info',
            field=models.TextField(blank=True, default='', verbose_name='Synaglar hakda maglumat'),
        ),
    ]
