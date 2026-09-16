# -*- coding: utf-8 -*-
"""
Synagchy - başlangyç mağlumatlary döretmek skripti.
Işlediş (UTF-8 bilen):
  PYTHONIOENCODING=utf-8 venv\\Scripts\\python seed_data.py
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from app.infrastructure.database.models import (
    University, Faculty, Specialty, SpecialtyRegionAdmission,
    EntranceExam, Subject, Question,
    Lecture, LectureTopic, ExamResult, Subscription,
    Region,
)

User = get_user_model()

# --- Köne mağlumatlary pozmak (täzeden dogry döretmek üçin) ---
print('Köne mağlumatlar pozdylýar...')
LectureTopic.objects.all().delete()
Lecture.objects.all().delete()
Question.objects.all().delete()
Subject.objects.all().delete()
EntranceExam.objects.all().delete()
SpecialtyRegionAdmission.objects.all().delete()
Specialty.objects.all().delete()
Region.objects.all().delete()
Faculty.objects.all().delete()
University.objects.all().delete()
Subscription.objects.all().delete()
ExamResult.objects.all().delete()
# Ulanyjylar (admin däl) - täzeden döretmek üçin pozdýarys
User.objects.filter(is_superuser=False).delete()

# --- Superuser döretmek (eýýäm bar bolsa, sakla) ---
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@synagchy.com',
        password='admin123',
        first_name='Administrator',
        last_name='',
    )
    print('Superuser döredildi: admin / admin123')
else:
    print('Superuser eýýäm bar: admin')

# --- Etralar (regionlar) ---
regions = {
    'Aşgabat': 'Türkmenistanyň baş şäheri',
    'Mary': 'Mary şäheri we regionu',
    'Lebap': 'Lebap merkezji bölümmeriri',
    'Daşoguz': 'Daşoguz şäheri we regionu',
    'Balkan': 'Balkan merkezji bölümmeriri',
}
region_objs = {}
for name, desc in regions.items():
    r, _ = Region.objects.get_or_create(name=name, defaults={'description': desc})
    region_objs[name] = r
    print(f'Region döredildi: {name}')

# --- Mysal ulanyjylar ---
users = [
    ('nepes', 'nepes@example.com', 'Nepes', 'Babamuradow', '12345', 'Aşgabat'),
    ('merdan', 'merdan@example.com', 'Merdan', 'Gurbangulyyew', '12345', 'Mary'),
    ('aygul', 'aygul@example.com', 'Aygül', 'Baýramowa', '12345', 'Lebap'),
]
for username, email, first_name, last_name, pwd, region_name in users:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username, email=email, first_name=first_name, last_name=last_name,
            password=pwd, region=region_objs[region_name]
        )
        print(f'Ulanyjy döredildi: {username} / {pwd} (region: {region_name})')

# --- Universitetler ---
unis = [
    University.objects.create(
        name='Magtymguly adyndaky Türkmen döwlet uniwersiteti',
        city='Aşgabat',
        description='Türkmenistanyň baş uniwersiteti',
    ),
    University.objects.create(
        name='Türkmen döwlet ykdysadyýet we dolandyryş instituty',
        city='Aşgabat',
        description='Ykdysadyýet instituty',
    ),
    University.objects.create(
        name='Türkmen döwlet medisina instituty',
        city='Aşgabat',
        description='Medisina instituty',
    ),
    University.objects.create(
        name='Türkmen politehniki instituty',
        city='Aşgabat',
        description='Politehniki institut',
    ),
]
print(f'{len(unis)} uniwersitet döredildi')

# --- Fakultetler ---
faculties = [
    Faculty.objects.create(university=unis[0], name='Fizika fakulteti', description='Fizika ugry boýunça'),
    Faculty.objects.create(university=unis[0], name='Matematika fakulteti', description='Matematika ugry boýunça'),
    Faculty.objects.create(university=unis[0], name='Filologiýa fakulteti', description='Dil we edebiýat'),
    Faculty.objects.create(university=unis[1], name='Ykdysadyýet fakulteti', description='Ykdysadyýet ugry'),
    Faculty.objects.create(university=unis[3], name='Inžener fakulteti', description='Inženerlik ugry'),
]
print(f'{len(faculties)} fakultet döredildi')

# --- Hünärler ---
specialties = [
    Specialty.objects.create(faculty=faculties[0], name='Radiofizika we elektronika', description='Radiofizika ugry'),
    Specialty.objects.create(faculty=faculties[0], name='Fizika mugallymçylygy', description='Fizika mugallymçylygy'),
    Specialty.objects.create(faculty=faculties[1], name='Matematika', description='Matematika'),
    Specialty.objects.create(faculty=faculties[2], name='Türkmen dili we edebiýaty', description='Dil we edebiýat'),
    Specialty.objects.create(faculty=faculties[3], name='Ykdysadyýet', description='Ykdysadyýet'),
]
print(f'{len(specialties)} hünär döredildi')

# --- Hünäre görä etrap boýunça giriş maglumatlary ---
from datetime import datetime
import pytz
tz = pytz.UTC

# Helper to create per-region admission configs
def create_region_admissions(specialty, region_data_list):
    for region, capacity, apps, start_at in region_data_list:
        SpecialtyRegionAdmission.objects.create(
            specialty=specialty,
            region=region,
            admission_capacity=capacity,
            applications_count=apps,
            exam_start_at=start_at,
        )

# Radiofizika we elektronika (specialties[0])
create_region_admissions(specialties[0], [
    (region_objs['Aşgabat'], 25, 120, tz.localize(datetime(2026, 10, 15, 10, 0))),
    (region_objs['Mary'], 10, 45, tz.localize(datetime(2026, 10, 16, 10, 0))),
    (region_objs['Lebap'], 10, 38, tz.localize(datetime(2026, 10, 17, 10, 0))),
])
# Fizika mugallymçylygy (specialties[1])
create_region_admissions(specialties[1], [
    (region_objs['Aşgabat'], 30, 150, tz.localize(datetime(2026, 10, 15, 14, 0))),
    (region_objs['Mary'], 12, 55, tz.localize(datetime(2026, 10, 16, 14, 0))),
    (region_objs['Daşoguz'], 8, 33, tz.localize(datetime(2026, 10, 17, 14, 0))),
])
# Matematika (specialties[2])
create_region_admissions(specialties[2], [
    (region_objs['Aşgabat'], 20, 90, tz.localize(datetime(2026, 10, 15, 9, 0))),
    (region_objs['Balkan'], 5, 22, tz.localize(datetime(2026, 10, 18, 9, 0))),
])
# Ykdysadyýet (specialties[4])
create_region_admissions(specialties[4], [
    (region_objs['Aşgabat'], 35, 200, tz.localize(datetime(2026, 10, 16, 11, 0))),
    (region_objs['Mary'], 15, 70, tz.localize(datetime(2026, 10, 17, 11, 0))),
])
print(f'Spetsialtasga etrap boýunça giriş maglumatlary döredildi')

# --- Giriş synaglary ---
exams = [
    EntranceExam.objects.create(specialty=specialties[0], title='Fizika synagy', description='Fizikadan giriş synagy'),
    EntranceExam.objects.create(specialty=specialties[0], title='Matematika synagy', description='Matematikadan giriş synagy'),
    EntranceExam.objects.create(specialty=specialties[1], title='Fizika synagy', description='Fizikadan giriş synagy'),
    EntranceExam.objects.create(specialty=specialties[3], title='Matematika synagy', description='Matematikadan giriş synagy'),
]
print(f'{len(exams)} synag döredildi')

# --- Dersler ---
subjects = [
    Subject.objects.create(name='Fizika', max_score=100),
    Subject.objects.create(name='Matematika', max_score=100),
    Subject.objects.create(name='Matematika', max_score=100),
    Subject.objects.create(name='Fizika', max_score=100),
    Subject.objects.create(name='Matematika', max_score=100),
]
for subject, exam in zip(subjects, exams):
    subject.exams.add(exam)
print(f'{len(subjects)} ders döredildi')

# --- Soraglar ---
questions = [
    Question.objects.create(subject=subjects[0], text='Nyutonyň 1-nji kanuny näme?',
                            option_a='Inersia', option_b='Täsir we garşylyk',
                            option_c='Dogrylyk', option_d='Güýç', correct_answer='A'),
    Question.objects.create(subject=subjects[0], text='Fizikada iş (A) nähili hasaplanýar?',
                            option_a='A = F·s', option_b='A = m·v',
                            option_c='A = F/v', option_d='A = m·a', correct_answer='A'),
    Question.objects.create(subject=subjects[1], text='2 + 2 = ?',
                            option_a='3', option_b='4', option_c='5', option_d='6', correct_answer='B'),
    Question.objects.create(subject=subjects[1], text='x² = 9 bolsa, x = ?',
                            option_a='3 we -3', option_b='9', option_c='0', option_d='81', correct_answer='A'),
]
print(f'{len(questions)} sorag döredildi')

print()
print('== BAŞLANGYÇ MAĞLUMATLAR DÖREDİLDİ ==')
print('Admin: admin / admin123')
print('Ulanyjylar: nepes/12345 (Aşgabat), merdan/12345 (Mary), aygul/12345 (Lebap)')
