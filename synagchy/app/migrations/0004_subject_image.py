from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_specialty_application_deadline_exam_start_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='subjects/images/'),
        ),
    ]
