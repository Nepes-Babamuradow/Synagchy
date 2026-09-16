from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_specialty_admission_and_university_about'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlanPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(choices=[('free', 'Free'), ('premium', 'Premium'), ('vip', 'VIP')], default='premium', help_text='Abuna görnüşi', max_length=20, unique=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, help_text='Abuna bahasy (TMT)', max_digits=10)),
                ('is_active', models.BooleanField(default=True, help_text='Bu baha işjeň bolsunmy?')),
                ('description', models.TextField(blank=True, default='', help_text='Abuna barada goşmaça maglumat')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
