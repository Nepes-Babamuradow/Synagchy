from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_university_exam_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialty',
            name='admission_capacity',
            field=models.IntegerField(default=0, verbose_name='Kabul edilmeli talyp sany'),
        ),
        migrations.AddField(
            model_name='specialty',
            name='applications_count',
            field=models.IntegerField(default=0, verbose_name='Tabşyrylanlaryň sany'),
        ),
        migrations.AddField(
            model_name='university',
            name='about',
            field=models.TextField(blank=True, default='', verbose_name='Universitet barada umumy maglumat'),
        ),
    ]
