# TODO — Synag platformasy üýtgeşmeleri

## 1. ExamResult model bugyny düzetmek
- [x] `ExamResult.exam` meýdanyna `null=True, blank=True` goşmak (exam ýok bolanda-da netije saklanar)
- [x] Täze migrasiýa döretmek (exam null bolup bilýär)

## 2. Specialty döredilende 2–5 ders birikdirmek
- [x] `SubjectNestedCreateSerializer.max_score` → `allow_null=True, required=False`
- [x] `ExamNestedCreateSerializer.create` — boş (blank/None) dersleri işledip geçmek
- [x] `SpecialtySerializer.validate` — boş däl dersleriň sany 2–5 aralygynda bolmaly
- [x] `SpecialtySerializer.create` — boş dersleri işledip geçmek

## 3. Exams pagination we filtr
- [x] `ExamListView.get` → `StandardPagination` + `PAGE_PARAMS` goşmak
- [x] `?specialty=<id>` parametri bilen synaglary aýyrmak (separate/filter)
- [x] `SpecialtyDetailView.get` → `ExamDetailSerializer` ulanyp, hünär saýlanylanda degişli dersler bile gelsin

## 4. Submit-answer (test ugratmak) hemme jogap bilen
- [x] Backend soraglary barlap, dogry/ýalňyş jogaplary gaýtarsyn
- [x] exam=None bolanda-da netije saklansyn (bug düzedildi)
- [x] `SubmitAnswerResponseSerializer` — dogry jogap sanawy goşmak

## 5. GraphQL
- [x] `subjectsBySpecialty` sorgusyny goşmak (frontend hünär saýlanylanda dersleri alsyn)
- [x] GraphQL `submit_answer` — exam=None bugyny düzetmek

## 6. Swagger dokumentasiýa
- [x] Submit-answer API dogry we düşnükli görkezmek (swagger)
- [x] Exams list pagination we specialty filtr swaggerde görkezmek
