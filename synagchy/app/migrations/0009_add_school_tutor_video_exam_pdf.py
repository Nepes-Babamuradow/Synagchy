from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_subscription_plan_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnlineTutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField(max_length=2048)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VideoLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(max_length=2048)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=512, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='school',
            name='subjects',
            field=models.ManyToManyField(blank=True, related_name='schools', to='app.Subject'),
        ),
        migrations.AddField(
            model_name='subject',
            name='exam_pdf',
            field=models.FileField(blank=True, null=True, upload_to='subjects/exams/'),
        ),
    ]
