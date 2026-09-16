# Synagchy - Frontend API Dokumentasiýasy

Bu dokument, **Synagchy** talyp platformasynyň backend API-leri bilen işleýän frontend geliştiriciler üçin düzüldi.

- **Base URL (REST):** `http://localhost:8000/api/v1/`
- **GraphQL:** `http://localhost:8000/graphql/`
- **Admin panel:** `http://localhost:8000/admin/`

---

## 10. Swagger (API Dokumentasiýasy)

API-iň doly dokumentasiýasyna **Swagger UI** bilen girip bilersiňiz:

- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`
- **OpenAPI JSON:** `http://localhost:8000/swagger.json`

Swagger UI-de ähli API endpoint'leri, olaryň **body** (istek) we **cevap** formatlary, parametrleri we token talaby görkezilýär. Záhmеt çekmän, her bir endpoint-i gönüden-göni **"Try it out"** bilen synap bilersiňiz.

> **Bellik:** Swagger UI doly düşnükli we interaktiw — API-i beryän adama hiç hili düşündiriş gerek däl. Hemme zat görünýär.

---

## 9. Docker-e goýmak (Docker Deployment)

Proýekti Docker bilen işletmek üçin (PostgreSQL + Django) şu ädimleri ýerine ýetiriň:

### 9.1 Talap (Requirements)
- Sisteme **Docker** we **Docker Compose** gurlan bolmaly.
- Docker gurlanlygyny barlamak:
```bash
docker --version
docker-compose --version
```

### 9.2 Docker faýllary
Proýektiň içinde (manage.py ýerleşýän ýerde) şu faýllar döredildi:
| Faýl | Düşündiriş |
|------|------------|
| `Dockerfile` | Django app-ni image döredýär |
| `docker-compose.yml` | PostgreSQL + Django serwisleri |
| `.dockerignore` | Image-e girmejek faýllar |

### 9.3 Docker Compose bilen işletmek

Birinji gezek (build + işletmek):
```bash
cd synagchy
docker-compose up --build
```

Öňe (bilden):
```bash
docker-compose up -d
```

Işleýän konteýnerleri görmek:
```bash
docker-compose ps
```

Loglary görmek:
```bash
docker-compose logs -f web
```

Itemini goýmak (stop):
```bash
docker-compose down
```

Data bazasyny hem pozmak üçin:
```bash
docker-compose down -v
```

### 9.4 Nähili işleýär?

- **`db` serwisi** — PostgreSQL 16 bazasyny işledýär (port `5433`).
- **`web` serwisi** — Django-ni gunicorn bilen işledýär (port `8000`).
- `web` başlamazdan öň `migrate` işledip, bazany döredýär.

### 9.5 Girmek (Access)
- **Frontend / API:** `http://localhost:8000`
- **Admin panel:** `http://localhost:8000/admin/`
- **GraphQL:** `http://localhost:8000/graphql/`

### 9.6 Admin ulanyjy döretmek
Konteýneriň içinde admin döretmek üçin:
```bash
docker-compose exec web python manage.py createsuperuser
```

### 9.7 Migrate / makemigrations
Täze migration döretsek:
```bash
docker-compose exec web python manage.py makemigrations app
docker-compose exec web python manage.py migrate
```

### 9.8 Environment üýtgetmek
`settings.py` database maglumatlary `os.environ`-den alýar. `docker-compose.yml` içinde `environment` bölüminde üýtgedip bilersiňiz:
```yaml
environment:
  DB_NAME: synagchy
  DB_USER: nepes
  DB_PASSWORD: 2704
  DB_HOST: db
  DB_PORT: 5432
```

> **Bellik:** `DB_HOST` Docker-de `db` (postgres serwis ady) bolmaly. Lokal (Docker-siz) işledeňde `localhost` bolmaly.

### 9.9 Media / Static faýllar
- **Media** (surat, audio, wideo, pdf) — `media_volume` volume-da saklanýar.
- **Static** (CSS/JS) — `static_volume` volume-da saklanýar.
- Bu volumelar konteýner pozulsa-da saklanýar.

---

## 1. Umumy maglumat

### 1.1 Autentifikasiýa (JWT)

Ulgam **JWT (JSON Web Token)** autentifikasiýany ulanýar. Girmekden soň siz **access** we **refresh** token alýarsyňyz.

- **Access token** — 1 gün güýjünli.
- **Refresh token** — 7 gün güýjünli.

**Token ulanyşy:** Her API soragyň **Authorization** header-inde goýmaly:

```
Authorization: Bearer <access_token>
```

**Refresh token** gutaranda:

```
POST /api/v1/auth/token/refresh/
Body (JSON):
{
  "refresh": "<refresh_token>"
}
```

Cevap:
```json
{ "access": "yeni_access_token" }
```

---

## 2. REST API Endpoint'leri

### 2.1 Awt (Auth)

#### ➕ Registrasiýa (Täze hasap)
`POST /api/v1/auth/register/`

**Body (JSON):**
```json
{
  "username": "ali",
  "email": "ali@mail.com",
  "full_name": "Ali Annayew",
  "phone": "+99361xxxxxxx",
  "password": "gizlinsöz"
}
```

**Cevap (201):**
```json
{
  "user": {
    "id": 1,
    "username": "ali",
    "email": "ali@mail.com",
    "full_name": "Ali Annayew",
    "phone": "+99361xxxxxxx",
    "rating": 0,
    "subscription_rank": 0
  },
  "refresh": "refresh_token",
  "access": "access_token"
}
```

#### 🔐 Girmek (Login)
`POST /api/v1/auth/login/`

**Body (JSON):**
```json
{
  "username": "ali",
  "password": "gizlinsöz"
}
```

**Cevap (200):**
```json
{
  "user": { "id": 1, "username": "ali", "email": "ali@mail.com", "full_name": "Ali Annayew", "phone": "+99361xxxxxxx", "rating": 0, "subscription_rank": 0 },
  "refresh": "refresh_token",
  "access": "access_token"
}
```

> Alternatiw: Standart JWT endpoint'leri hem bar:
> - `POST /api/v1/auth/token/` — `{username, password}` → `{access, refresh}`
> - `POST /api/v1/auth/token/refresh/` — `{refresh}` → `{access}`

---

### 2.2 Ulanyjylar (Users)

#### 👥 Ulanyjylaryň sanawy (reýting boýunça)
`GET /api/v1/users/`

**Cevap (200):**
```json
[
  {
    "id": 1,
    "username": "ali",
    "email": "ali@mail.com",
    "full_name": "Ali Annayew",
    "phone": "+99361xxxxxxx",
    "rating": 85,
    "subscription_rank": 0
  }
]
```

#### 👤 Ulanyjy jikme-jigi
`GET /api/v1/users/{id}/`

**Cevap (200):** Ýokardaky ýaly bir ulanyjy.

> **Bellik:** Endi ulanyjy maglumatlaryna hünärine degişli **universitet**, **fakultet** we **hünär** ady hem goşuldy:
> - `specialty` — hünäriň ID-si
> - `specialty_name` — hünäriň ady
> - `faculty_name` — fakultetiň ady
> - `university_name` — uniwersitetiň ady

**Cevap mysaly:**
```json
{
  "id": 1,
  "username": "ali",
  "specialty": 3,
  "specialty_name": "Radiofizika we Elektronika",
  "faculty_name": "Fizika fakulteti",
  "university_name": "Magtymguly adyndaky TDU",
  "email": "ali@mail.com",
  "full_name": "Ali Annayew",
  "phone": "+99361xxxxxxx",
  "rating": 85,
  "subscription_rank": 0
}
```

#### 🏛️ Meniň hünärim boýunça uniwersitetim (token gerek)
`GET /api/v1/my-university/`

**Header:** `Authorization: Bearer <access_token>`

Loginden soň, ulanyjynyň **hünärine** görä onuň **hünäri, fakulteti we uniwersiteti** jikme-jik görkezýär.

**Cevap (200):**
```json
{
  "user": 1,
  "username": "ali",
  "specialty": {
    "id": 3,
    "name": "Radiofizika we Elektronika",
    "description": "..."
  },
  "faculty": {
    "id": 2,
    "name": "Fizika fakulteti",
    "description": "..."
  },
  "university": {
    "id": 1,
    "name": "Magtymguly adyndaky TDU",
    "city": "Aşgabat",
    "description": "..."
  }
}
```

> Eger ulanyjynyň hünäri kesgitlenmedik bolsa, `404` (hünäri ýok) habary berýär.

---

### 2.3 Reýting (Rating)

#### 🏆 Reýting tablisasy (Top 3-e yenillik bilen)
`GET /api/v1/rating/`

**Cevap (200):**
```json
[
  {
    "id": 1,
    "username": "ali",
    "rating": 95,
    "rank": 1,
    "discount": "50%"
  },
  {
    "id": 2,
    "username": "meret",
    "rating": 80,
    "rank": 2,
    "discount": "30%"
  },
  {
    "id": 3,
    "username": "nur",
    "rating": 70,
    "rank": 3,
    "discount": "20%"
  }
]
```

> **Ýenillik:** 1-nji orun → 50%, 2-nji → 30%, 3-nji → 20%.

---

### 2.4 Universitetler (Universities)

#### 🏛️ Universitetleriň sanawy
`GET /api/v1/universities/`

**Cevap (200):**
```json
[
  { "id": 1, "name": "Magtymguly adyndaky TDU", "city": "Aşgabat", "description": "..." }
]
```

`POST /api/v1/universities/` — täze uniwersitet goşmak (admin).

#### 🏛️ Universitet jikme-jigi (fakultetler bilen)
`GET /api/v1/universities/{id}/`

**Cevap (200):**
```json
{
  "id": 1,
  "name": "Magtymguly adyndaky TDU",
  "city": "Aşgabat",
  "description": "...",
  "faculties": [
    { "id": 1, "university": 1, "university_name": "Magtymguly adyndaky TDU", "name": "Fizika fakulteti", "description": "..." }
  ]
}
```

---

### 2.5 Fakultetler (Faculties)

#### 🎓 Fakultetleriň sanawy
`GET /api/v1/faculties/`

```json
[
  { "id": 1, "university": 1, "university_name": "Magtymguly adyndaky TDU", "name": "Fizika fakulteti", "description": "..." }
]
```

#### 🎓 Fakultet jikme-jigi (hünärler bilen)
`GET /api/v1/faculties/{id}/`

```json
{
  "id": 1,
  "university": 1,
  "university_name": "Magtymguly adyndaky TDU",
  "name": "Fizika fakulteti",
  "description": "...",
  "specialties": [
    { "id": 1, "faculty": 1, "faculty_name": "Fizika fakulteti", "university_name": "Magtymguly adyndaky TDU", "name": "Hasaplaýyş fizikasy", "description": "..." }
  ]
}
```

---

### 2.6 Hünärler (Specialties)

#### 📚 Hünärleriň sanawy
`GET /api/v1/specialties/`

#### 📚 Hünär jikme-jigi (synaglar bilen)
`GET /api/v1/specialties/{id}/`

```json
{
  "id": 1,
  "faculty": 1,
  "faculty_name": "Fizika fakulteti",
  "university_name": "Magtymguly adyndaky TDU",
  "name": "Hasaplaýyş fizikasy",
  "description": "...",
  "exams": [
    { "id": 1, "specialty": 1, "specialty_name": "Hasaplaýyş fizikasy", "faculty_name": "Fizika fakulteti", "university_name": "Magtymguly adyndaky TDU", "title": "Giriş synagy", "description": "..." }
  ]
}
```

---

### 2.7 Giriş synaglary (Entrance Exams)

#### 📝 Synaglaryň sanawy
`GET /api/v1/exams/`

```json
[
  {
    "id": 1,
    "specialty": 1,
    "specialty_name": "Hasaplaýyş fizikasy",
    "faculty_name": "Fizika fakulteti",
    "university_name": "Magtymguly adyndaky TDU",
    "title": "Giriş synagy",
    "description": "..."
  }
]
```

#### 📝 Synag jikme-jigi (dersler bilen)
`GET /api/v1/exams/{id}/`

```json
{
  "id": 1,
  "specialty": 1,
  "specialty_name": "Hasaplaýyş fizikasy",
  "faculty_name": "Fizika fakulteti",
  "university_name": "Magtymguly adyndaky TDU",
  "title": "Giriş synagy",
  "description": "...",
  "subjects": [
    { "id": 1, "exam": 1, "name": "Fizika", "max_score": 30 }
  ]
}
```

---

### 2.8 Dersler (Subjects)

#### 📖 Dersleriň sanawy
`GET /api/v1/subjects/`

```json
[
  { "id": 1, "exam": 1, "name": "Fizika", "max_score": 30 }
]
```

---

### 2.9 Soraglar (Questions)

#### ❓ Ähli soraglar
`GET /api/v1/questions/`

#### ❓ Bir dersiň soraglary
`GET /api/v1/subjects/{subject_id}/questions/`

```json
[
  {
    "id": 1,
    "subject": 1,
    "text": "Nyutonyň birinji kanuny näme?",
    "option_a": "Inersiýa kanuny",
    "option_b": "Täsir we täsire garşylyk",
    "option_c": "Energetikanyň saklanysy",
    "option_d": "Impuls"
  }
]
```

> **Bellik:** Dogry jogap bu endpoint'de **görünmeýär** (frontend soragy çözýär, jogap bilen bir bile serwerde barlanylýar).

---

### 2.10 Jogap ibermek (Submit Answer)

#### ✅ Sorag çözmek (token gerek)
`POST /api/v1/submit-answer/`

**Header:** `Authorization: Bearer <access_token>`

**Body (JSON):**
```json
{
  "subject_id": 1,
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C"
  }
}
```

**Cevap (200):**
```json
{
  "correct_count": 2,
  "total_count": 3,
  "score": 67,
  "rating": 67
}
```

> **Düşündiriş:**
> - `score` = dogry jogap (%) — `(correct_count / total_count) * 100`
> - `rating` = ulanyjynyň iň gowy netijesi (reýting tablisasyna goşulýar)

---

### 2.11 Netijeler (Results)

#### 📊 Ähli netijeler (reýting boýunça)
`GET /api/v1/results/`

```json
[
  {
    "id": 1,
    "user": 1,
    "exam": 1,
    "score": 67,
    "correct_count": 2,
    "total_count": 3,
    "created_at": "2026-08-05T10:00:00Z"
  }
]
```

#### 📊 Meniň netijelerim (token gerek)
`GET /api/v1/my-results/`

**Header:** `Authorization: Bearer <access_token>`

**Cevap:** Diňe öz netijeleriňiz.

---

### 2.12 Abuna (Subscription)

#### 📦 Abuna maglumaty (token gerek)
`GET /api/v1/subscription/`

**Header:** `Authorization: Bearer <access_token>`

**Cevap (200):**
```json
{
  "id": 1,
  "user": 1,
  "plan": "free",
  "is_active": true,
  "started_at": "2026-08-05T10:00:00Z",
  "expires_at": null
}
```

#### 📦 Abuna satyn almak / täzelemek (token gerek)
`POST /api/v1/subscription/`

**Header:** `Authorization: Bearer <access_token>`

**Body (JSON):**
```json
{
  "plan": "premium"
}
```

**Cevap (200):**
```json
{
  "id": 1,
  "user": 1,
  "plan": "premium",
  "is_active": true,
  "started_at": "2026-08-05T10:00:00Z",
  "expires_at": null,
  "discount_percent": 50
}
```

> **Bellik:** `discount_percent` — ulanyjy reýtingde ilkinji 5-de bolsa, pozy görkezilýär (1-50%, 2-30%, 3-20%).

---

### 2.13 Bank tölegi (Payment)

#### 💳 Töleg başlatmak (token gerek)
`POST /api/v1/payment/`

**Header:** `Authorization: Bearer <access_token>`

**Body (JSON):**
```json
{
  "plan": "premium"
}
```

**Cevap (200):**
```json
{
  "id": 1,
  "user": 1,
  "user_username": "ali",
  "plan": "premium",
  "amount": 100,
  "discount_percent": 50,
  "final_amount": 50,
  "bank_ref": "BANK-abc123",
  "status": "pending",
  "created_at": "2026-08-05T10:00:00Z"
}
```

> **Düşündiriş:**
> - `amount` — abunanyň asyl bahasy (yenilliksiz)
> - `discount_percent` — ulanyjynyň reýtingine görä yenilligi (1-50%, 2-30%, 3-20%)
> - `final_amount` — yenillik ulanylan soňky baha: `amount × (100 - discount) / 100`
> - `bank_ref` — bank API-dan gelen töleg referans belgisi
> - `status` — `pending` (garşylýar), `paid` (töledi), `failed`, `refunded`

Töleg başlananda, ulanyjy bank sahypasyna gönükdirilýär (bank API-de ýerine ýetirilýär).

#### ✅ Töleg tassyknamasy / webhook (tölenenden soň premium bermek)
`POST /api/v1/payment/confirm/`

**Body (JSON):**
```json
{
  "bank_ref": "BANK-abc123"
}
```

**Cevap (200):**
```json
{
  "status": "paid",
  "plan": "premium",
  "subscription": {
    "id": 1,
    "user": 1,
    "plan": "premium",
    "is_active": true,
    "started_at": "2026-08-05T10:00:00Z",
    "expires_at": "2026-09-04T10:00:00Z"
  }
}
```

> **Düşündiriş:** Bank tölegi tassyklaýar we ulanyja **premium** abunany berýär (30 gün). Bu endpoint-i bank API webhook-y çagyrýar.

#### 📜 Töleg taryhy (token gerek)
`GET /api/v1/payment/`

**Header:** `Authorization: Bearer <access_token>`

**Cevap (200):** Ulanyjynyň ähli tölegleriniň sanawy.

> **⚠️ Bank API bellik:** `app/presentation/rest/v1/payment.py` faýlynda `_bank_api_initiate` funksiýasy bar. Häzirlikçe **placeholder** (mock) ulanýar. Hakyky bank API-e birikdirmek üçin şol funksiýanyň içindäki `requests` kody işjeňleşdirilmeli.

---

## 3. GraphQL API

GraphQL endpoint'i: `POST http://localhost:8000/graphql/`

### 3.1 Query'lar

#### Barlan (kitap) — ähli ulanyjylar
```graphql
query {
  users {
    id
    username
    email
    full_name
    rating
    subscription_rank
  }
}
```

#### Universitetler
```graphql
query {
  universities { id name city description }
}
```

#### Fakultetler
```graphql
query {
  faculties { id university_id name description }
}
```

#### Hünärler
```graphql
query {
  specialties { id faculty_id name description }
}
```

#### Synaglar
```graphql
query {
  exams { id specialty_id title description }
}
```

#### Hünäre görä synaglar
```graphql
query {
  examsBySpecialty(specialtyId: 1) { id title }
}
```

#### Dersler
```graphql
query {
  subjects { id exam_id name max_score }
}
```

#### Synaga görä dersler
```graphql
query {
  subjectsByExam(examId: 1) { id name max_score }
}
```

#### Derse görä temalar (leksiýa)
```graphql
query {
  topicsBySubject(subjectId: 1) {
    id subject_id title description order
  }
}
```

#### Temaga görä leksiýalar
```graphql
query {
  lecturesByTopic(topicId: 1) {
    id topic_id title content_type content_text image_url pdf_url audio_url video_url order
  }
}
```

#### Derse görä soraglar
```graphql
query {
  questionsBySubject(subjectId: 1) {
    id subject_id text option_a option_b option_c option_d
  }
}
```

#### Netijeler
```graphql
query {
  results { id user_id exam_id score correct_count total_count }
}
```

#### Abuna
```graphql
query {
  subscriptions { id user_id plan is_active }
}
```

#### Reýting (top-3 yenillik bilen)
```graphql
query {
  rating { rank user_id username rating discount }
}
```

### 3.2 Mutation'lar

#### Sorag çözmek
```graphql
mutation {
  submitAnswer(userId: 1, subjectId: 1, answers: "{\"1\": \"A\", \"2\": \"B\"}") {
    correct_count
    total_count
    score
    rating
  }
}
```

---

## 4. Data Modeller (Baza)

### 4.1 User (Ulanyjy)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| username | string | Ulanyjy ady |
| email | string | E-poçta |
| full_name | string | Doly ady |
| phone | string | Telefon |
| password | string (write-only) | Parol |
| rating | int | Reýting baly |
| subscription_rank | int | Abuna derejesi |

### 4.2 University (Universitet)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| name | string | Ady |
| city | string | Şäheri |
| description | text | Düşündiriş |

### 4.3 Faculty (Fakultet)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| university | int (FK) | Universitet |
| name | string | Ady |
| description | text | Düşündiriş |

### 4.4 Specialty (Hünär)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| faculty | int (FK) | Fakultet |
| name | string | Ady |
| description | text | Düşündiriş |

### 4.5 EntranceExam (Giriş synagy)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| specialty | int (FK) | Hünär |
| title | string | Ady |
| description | text | Düşündiriş |

### 4.6 Subject (Ders)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| exam | int (FK) | Synag |
| name | string | Ady |
| max_score | int | Iň ýokary bal |

### 4.7 Question (Sorag)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| subject | int (FK) | Ders |
| text | text | Sorag |
| option_a | string | A jogap |
| option_b | string | B jogap |
| option_c | string | C jogap |
| option_d | string | D jogap |
| correct_answer | string | Dogry jogap (A/B/C/D) — diňe admin görýär |

### 4.8 LectureTopic (Leksiýa temasy)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| subject | int (FK) | Ders |
| title | string | Temanyň ady |
| description | text | Düşündiriş |
| order | int | Tertip belgisi |

### 4.9 Lecture (Leksiýa)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| topic | int (FK) | Tema |
| title | string | Ady |
| content_type | string | `text` / `formula` / `image` / `audio` / `video` / `pdf` |
| content_text | text | Teksti (text/formula üçin) |
| image | file | Surat (image üçin) |
| audio | file | Saz (audio üçin) |
| video | file | Wideo (video üçin) |
| pdf_file | file | PDF (pdf üçin) |
| order | int | Tertip belgisi |

**content_type görä görkezilişi:**
- `text` → `content_text` görkez
- `formula` → `content_text` (formula) görkez
- `image` → `image_url` görkez
- `audio` → `audio_url` (player bilen)
- `video` → `video_url` (player bilen)
- `pdf` → `pdf_url` (PDF brauzerde)

### 4.10 ExamResult (Netije)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| user | int (FK) | Ulanyjy |
| exam | int (FK) | Synag |
| score | int | Bal (%) |
| correct_count | int | Dogry sany |
| total_count | int | Umumy sany |
| created_at | datetime | Wagty |

### 4.11 Subscription (Abuna)
| Pole | Tip | Düşündiriş |
|------|-----|------------|
| id | int | ID |
| user | int (FK) | Ulanyjy |
| plan | string | `free` / `premium` / ... |
| is_active | bool | Işjeňligi |
| started_at | datetime | Başlanan wagty |
| expires_at | datetime | Biteýen wagty |

---

## 5. Frontend iş yzygiderliligi (Flow)

### 5.1 Baş sahypa (Browze)
1. `GET /api/v1/universities/` — uniwersitetleri al
2. Ulanyjy uniwersitet saýla → `GET /api/v1/universities/{id}/` — fakultetler
3. Fakultet saýla → `GET /api/v1/faculties/{id}/` — hünärler
4. Hünär saýla → `GET /api/v1/specialties/{id}/` — synaglar
5. Synag saýla → `GET /api/v1/exams/{id}/` — dersler

### 5.2 Sorag çözmek
1. Ders saýla → `GET /api/v1/subjects/{subject_id}/questions/`
2. Ulanyjy jogaplary saýla
3. `POST /api/v1/submit-answer/` (token bilen) — netijäni hasapla

### 5.3 Leksiýa okamak
1. Ders saýla
2. `topicsBySubject(subjectId)` — temalary al (GraphQL)
3. Tema saýla → `lecturesByTopic(topicId)` — leksiýalary al
4. `content_type`-e görä dogry görkez

### 5.4 Abuna
1. `POST /api/v1/subscription/` (token bilen) — abuna satyn al
2. `GET /api/v1/rating/` — reýting we yenillikleri gör

---

## 6. Gysgaça Endpoint Tablitsasy

| Metod | Endpoint | Açyk (Public) / Token | Düşündiriş |
|-------|----------|----------------------|------------|
| POST | `/api/v1/auth/register/` | Açyk | Hajap açmak |
| POST | `/api/v1/auth/login/` | Açyk | Girmek |
| POST | `/api/v1/auth/token/` | Açyk | JWT token |
| POST | `/api/v1/auth/token/refresh/` | Açyk | Token täzelemek |
| GET | `/api/v1/users/` | Açyk | Ulanyjylar |
| GET | `/api/v1/users/{id}/` | Açyk | Ulanyjy |
| GET | `/api/v1/my-university/` | **Token** | Hünärim boýunça uniwersitet/fakultet |
| GET | `/api/v1/rating/` | Açyk | Reýting |
| GET | `/api/v1/universities/` | Açyk | Universitetler |
| GET | `/api/v1/universities/{id}/` | Açyk | Universitet + fakultetler |
| GET | `/api/v1/faculties/` | Açyk | Fakultetler |
| GET | `/api/v1/faculties/{id}/` | Açyk | Fakultet + hünärler |
| GET | `/api/v1/specialties/` | Açyk | Hünärler |
| GET | `/api/v1/specialties/{id}/` | Açyk | Hünär + synaglar |
| GET | `/api/v1/exams/` | Açyk | Synaglar |
| GET | `/api/v1/exams/{id}/` | Açyk | Synag + dersler |
| GET | `/api/v1/subjects/` | Açyk | Dersler |
| GET | `/api/v1/questions/` | Açyk | Ähli soraglar |
| GET | `/api/v1/subjects/{id}/questions/` | Açyk | Dersiň soraglary |
| POST | `/api/v1/submit-answer/` | **Token** | Sorag çözmek |
| GET | `/api/v1/results/` | Açyk | Ähli netijeler |
| GET | `/api/v1/my-results/` | **Token** | Meniň netijelerim |
| GET | `/api/v1/subscription/` | **Token** | Abuna maglumaty |
| POST | `/api/v1/subscription/` | **Token** | Abuna satyn almak |
| GET | `/api/v1/payment/` | **Token** | Töleg taryhy |
| POST | `/api/v1/payment/` | **Token** | Töleg başlatmak |
| POST | `/api/v1/payment/confirm/` | Bank API | Töleg tassyknamasy (webhook) |

---

## 7. Ýalňyşlyklar (Errors)

| Status kody | Düşündiriş |
|-------------|------------|
| 200 | Üstünlik |
| 201 | Döredildi (created) |
| 400 | Nädogry isleg (mysal: parol ýalňyş) |
| 401 | Token gerek / token ýalňyş |
| 404 | Tapylmady (not found) |

---

## 8. Gowulandyrmak üçin bellikler (Bonus)

- `GET /api/v1/subjects/` — dersiň sorag sanyny görkezmek üçin `question_count` goşmak maslahat berilýär.
- Frontend-de `discount` (50%, 30%, 20%) reýting sahypasynda görkezilmeli.
- Leksiýalary görkezende `content_type`-e görä fayl görnüşinde format saýlamak gerek.
