from django.contrib.auth import get_user_model

from app.infrastructure.database.models import (
    University, Faculty, Specialty, SpecialtyRegionAdmission,
    EntranceExam, Subject, Question,
    OnlineTutor, VideoLesson, School, Subscription,
    Region,
)


def create_initial_data():
    User = get_user_model()

    # Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin', email='admin@synagchy.com', password='admin123', first_name='Administrator', last_name=''
        )

    # Regions (etrap)
    region_defs = [
        ('Aşgabat', 'Türkmenistanyň baş şäheri'),
        ('Mary', 'Mary şäheri we regionu'),
        ('Lebap', 'Lebap merkezji bölümmeriri'),
        ('Daşoguz', 'Daşoguz şäheri we regionu'),
        ('Balkan', 'Balkan merkezji bölümmeriri'),
    ]
    regions = {}
    for name, desc in region_defs:
        r, _ = Region.objects.get_or_create(name=name, defaults={'description': desc})
        regions[name] = r

    # Sample users
    sample_users = [
        ('nepes', 'nepes@example.com', 'Nepes', 'Babamuradow', '12345', 'Aşgabat'),
        ('merdan', 'merdan@example.com', 'Merdan', 'Gurbangulyyew', '12345', 'Mary'),
        ('aygul', 'aygul@example.com', 'Aygül', 'Baýramowa', '12345', 'Lebap'),
    ]
    for username, email, first_name, last_name, pwd, region_name in sample_users:
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username, email=email, first_name=first_name, last_name=last_name,
                password=pwd, region=regions.get(region_name)
            )

    # Universities and faculties
    uni_defs = [
        ('Magtymguly adyndaky Türkmen döwlet uniwersiteti', 'Aşgabat'),
        ('Türkmen döwlet ykdysadyýet we dolandyryş instituty', 'Aşgabat'),
        ('Türkmen döwlet medisina instituty', 'Aşgabat'),
        ('Türkmen politehniki instituty', 'Aşgabat'),
    ]
    unis = {}
    for name, city in uni_defs:
        uni, _ = University.objects.get_or_create(name=name, defaults={'city': city, 'description': name})
        unis[name] = uni

    # Faculties
    fac_defs = [
        (unis[uni_defs[0][0]], 'Fizika fakulteti'),
        (unis[uni_defs[0][0]], 'Matematika fakulteti'),
        (unis[uni_defs[0][0]], 'Filologiýa fakulteti'),
        (unis[uni_defs[1][0]], 'Ykdysadyýet fakulteti'),
        (unis[uni_defs[3][0]], 'Inžener fakulteti'),
    ]
    facs = []
    for uni, name in fac_defs:
        f, _ = Faculty.objects.get_or_create(university=uni, name=name, defaults={'description': name})
        facs.append(f)

    # Specialties
    spec_defs = [
        (facs[0], 'Radiofizika we elektronika'),
        (facs[0], 'Fizika mugallymçylygy'),
        (facs[1], 'Matematika'),
        (facs[2], 'Türkmen dili we edebiýaty'),
        (facs[3], 'Ykdysadyýet'),
    ]
    specs = []
    for fac, name in spec_defs:
        s, _ = Specialty.objects.get_or_create(faculty=fac, name=name, defaults={'description': name})
        specs.append(s)

    # Per-region admission configs (Kabul edilmeli talyp sany, Tabşyrylanlaryň sany, Synagyň başlaýan wagty)
    from datetime import datetime
    import pytz
    tz = pytz.UTC

    def _ensure_region_admission(specialty, region_name, capacity, apps, start_at):
        SpecialtyRegionAdmission.objects.get_or_create(
            specialty=specialty,
            region=regions[region_name],
            defaults={
                'admission_capacity': capacity,
                'applications_count': apps,
                'exam_start_at': start_at,
            }
        )

    if specs and 'Aşgabat' in regions:
        _ensure_region_admission(specs[0], 'Aşgabat', 25, 120, tz.localize(datetime(2026, 10, 15, 10, 0)))
        _ensure_region_admission(specs[0], 'Mary', 10, 45, tz.localize(datetime(2026, 10, 16, 10, 0)))
        _ensure_region_admission(specs[1], 'Aşgabat', 30, 150, tz.localize(datetime(2026, 10, 15, 14, 0)))
        _ensure_region_admission(specs[2], 'Aşgabat', 20, 90, tz.localize(datetime(2026, 10, 15, 9, 0)))
        _ensure_region_admission(specs[4], 'Aşgabat', 35, 200, tz.localize(datetime(2026, 10, 16, 11, 0)))

    # Entrance exams, subjects and some example questions (idempotent)
    if specs:
        exam, _ = EntranceExam.objects.get_or_create(specialty=specs[0], title='Fizika synagy', defaults={'description': 'Fizikadan giriş synagy'})
        sub1, _ = Subject.objects.get_or_create(name='Fizika', defaults={'max_score': 100})
        sub2, _ = Subject.objects.get_or_create(name='Matematika', defaults={'max_score': 100})
        sub1.exams.add(exam)
        sub2.exams.add(exam)

        # Questions (20 sany)
        q_defs = [
            # Fizika (sub1) - 10 sany
            ('Nyutonyň 1-nji kanuny näme?', 'Inersia', 'Täsir we garşylyk', 'Dogrylyk', 'Güýç', 'A'),
            ('Fizikada iş (A) nähili hasaplanýar?', 'A = F·s', 'A = m·v', 'A = F/v', 'A = m·a', 'A'),
            ('Energiýa (E) nähili hasaplanýar?', 'E = m·c²', 'E = m·v²/2', 'E = F·s', 'E = p·v', 'A'),
            ('Güýç (F) nähili hasaplanýar?', 'F = m·a', 'F = m·v', 'F = m·v²', 'F = a/m', 'A'),
            ('Teleglik (g) nähili hasaplanýar?', 'g = G·M/R²', 'g = G·M·R²', 'g = G·M/R', 'g = G·M·R', 'A'),
            ('Sowuklyk (T) nähili hasaplanýar?', 'T = 2π·√(L/g)', 'T = 2π·√(g/L)', 'T = 2π·√(L·g)', 'T = 2π·√(L/g²)', 'A'),
            ('Elektrik güýcy (I) nähili hasaplanýar?', 'I = V/R', 'I = V·R', 'I = R/V', 'I = V²·R', 'A'),
            ('Güýç (P) nähili hasaplanýar?', 'P = W/t', 'P = W·t', 'P = t/W', 'P = W²/t', 'A'),
            ('Görnüş we çák edilişi (s) nähili hasaplanýar?', 's = v·t', 's = v/t', 's = t/v', 's = v²·t', 'A'),
            ('Görnüş we çák edilişi (v) nähili hasaplanýar?', 'v = s/t', 'v = s·t', 'v = t/s', 'v = s²·t', 'A'),
            # Matematika (sub2) - 10 sany
            ('(a+b)² nähili açylanýar?', 'a²+2ab+b²', 'a²-2ab+b²', 'a²+b²', 'a²-ab+b²', 'A'),
            ('(a-b)² nähili açylanýar?', 'a²-2ab+b²', 'a²+2ab+b²', 'a²-b²', 'a²+ab+b²', 'A'),
            ('a²-b² nähili çýyrylyýar?', '(a-b)(a+b)', '(a+b)(a-b)', '(a-b)(a+b)', '(a+b)(a-b)', 'A'),
            ('Sinus teorema nähili?', 'a/sinA = b/sinB = c/sinC', 'a/sinA = b/sinB = c/sinC', 'a/sinA = b/sinB = c/sinC', 'a/sinA = b/sinB = c/sinC', 'A'),
            ('Kosinus teorema nähili?', 'c² = a²+b²-2ab·cosC', 'c² = a²+b²+2ab·cosC', 'c² = a²-b²-2ab·cosC', 'c² = a²+b²-2ab·sinC', 'A'),
            ('Logarithm qanuny nähili?', 'log(ab) = log(a)+log(b)', 'log(ab) = log(a)-log(b)', 'log(ab) = log(a)·log(b)', 'log(ab) = log(a)/log(b)', 'A'),
            ('Deriwa nähili?', 'f\'(x) = lim h→0 (f(x+h)-f(x))/h', 'f\'(x) = lim h→0 (f(x+h)+f(x))/h', 'f\'(x) = lim h→0 (f(x)-f(x+h))/h', 'f\'(x) = lim h→0 (f(x+h)·f(x))/h', 'A'),
            ('Integral nähili?', 'F(x) = ∫f(x)dx', 'F(x) = ∫f(x)dx', 'F(x) = ∫f(x)dx', 'F(x) = ∫f(x)dx', 'A'),
            ('Geometriýa: aýlananyň ýüzümi (S) nähili?', 'S = π·r²', 'S = 2π·r', 'S = π·r', 'S = 2π·r²', 'A'),
            ('Geometriýa: şaryň koubuly (V) nähili?', 'V = 4/3·π·r³', 'V = 4/3·π·r²', 'V = 4/3·π·r', 'V = 4/3·π·r⁴', 'A'),
        ]

        for i, (text, a, b, c, d, ans) in enumerate(q_defs):
            subject = sub1 if i < 10 else sub2
            Question.objects.get_or_create(subject=subject, text=text, defaults={
                'option_a': a, 'option_b': b, 'option_c': c, 'option_d': d, 'correct_answer': ans
            })

    # Sample online tutors and video lessons
    OnlineTutor.objects.get_or_create(name='Repetitor A', defaults={'url': 'https://tutor.example.com/lesson/1', 'description': 'Onlaýn repetitor'} )
    VideoLesson.objects.get_or_create(title='Algebra basics', defaults={'url': 'https://video.example.com/abc', 'description': 'Algebra we matematika sapagy'})

    # Sample school
    school, _ = School.objects.get_or_create(name='10-njy mekdep', defaults={'address': 'Aşgabat'})
    # Link subjects to school if they exist
    try:
        first_subject = Subject.objects.first()
        if first_subject and not school.subjects.filter(pk=first_subject.pk).exists():
            school.subjects.add(first_subject)
    except Exception:
        pass

    # Subscription plan placeholders may be created elsewhere (admin). Ensure no exceptions if model absent.
    return True
