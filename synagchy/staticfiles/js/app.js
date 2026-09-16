// GraphQL endpoint
const GRAPHQL_URL = '/graphql/';

// Tab navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// GraphQL sorgusy iberiji
async function gql(query, variables = {}) {
    const res = await fetch(GRAPHQL_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, variables })
    });
    const data = await res.json();
    if (data.errors) throw new Error(data.errors[0].message);
    return data.data;
}

// Sahypa açylanda
document.addEventListener('DOMContentLoaded', () => {
    loadUniversities();
    loadFaculties();
    loadSpecialties();
    loadExams();
    loadSubjects();
    loadRating();
});

// ---------- UNIVERSITETLER ----------
async function loadUniversities() {
    const grid = document.getElementById('university-grid');
    try {
        const data = await gql(`{ universities { id name city description } }`);
        if (!data.universities.length) {
            grid.innerHTML = '<div class="empty">Universitet yok</div>';
            return;
        }
        grid.innerHTML = data.universities.map(u => `
            <div class="card" onclick="showFaculties(${u.id})">
                <h3>${u.name}</h3>
                <p>${u.city}</p>
                <p>${u.description || ''}</p>
                <span class="badge">Fakultetleri gormek →</span>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// ---------- FAKULTETLER ----------
async function loadFaculties() {
    const grid = document.getElementById('faculty-grid');
    try {
        const data = await gql(`{ faculties { id universityId name description } }`);
        if (!data.faculties.length) {
            grid.innerHTML = '<div class="empty">Fakultet yok</div>';
            return;
        }
        grid.innerHTML = data.faculties.map(f => `
            <div class="card" onclick="showSpecialties(${f.id})">
                <h3>${f.name}</h3>
                <p>${f.description || ''}</p>
                <span class="badge">Hunarleri gormek →</span>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Uniweristet basylanda sol uniweristetin fakultetlerini gorkez
async function showFaculties(universityId) {
    const grid = document.getElementById('faculty-grid');
    try {
        const data = await gql(`{ faculties { id universityId name description } }`);
        const list = data.faculties.filter(f => f.universityId === universityId);
        if (!list.length) {
            grid.innerHTML = '<div class="empty">Bu uniweristetde fakultet yok</div>';
        } else {
            grid.innerHTML = list.map(f => `
                <div class="card" onclick="showSpecialties(${f.id})">
                    <h3>${f.name}</h3>
                    <p>${f.description || ''}</p>
                    <span class="badge">Hunarleri gormek →</span>
                </div>
            `).join('');
        }
        switchTab('faculties');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// ---------- HUNARLER ----------
async function loadSpecialties() {
    const grid = document.getElementById('specialty-grid');
    try {
        const data = await gql(`{ specialties { id facultyId name description } }`);
        if (!data.specialties.length) {
            grid.innerHTML = '<div class="empty">Hunar yok</div>';
            return;
        }
        grid.innerHTML = data.specialties.map(s => `
            <div class="card" onclick="showExams(${s.id})">
                <h3>${s.name}</h3>
                <p>${s.description || ''}</p>
                <span class="badge">Synaglary gormek →</span>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Fakultet basylanda sol fakultetin hunarlerini gorkez
async function showSpecialties(facultyId) {
    const grid = document.getElementById('specialty-grid');
    try {
        const data = await gql(`{ specialties { id facultyId name description } }`);
        const list = data.specialties.filter(s => s.facultyId === facultyId);
        if (!list.length) {
            grid.innerHTML = '<div class="empty">Bu fakultetde hunar yok</div>';
        } else {
            grid.innerHTML = list.map(s => `
                <div class="card" onclick="showExams(${s.id})">
                    <h3>${s.name}</h3>
                    <p>${s.description || ''}</p>
                    <span class="badge">Synaglary gormek →</span>
                </div>
            `).join('');
        }
        switchTab('specialties');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// ---------- SYNAGLAR ----------
async function loadExams() {
    const grid = document.getElementById('exam-grid');
    try {
        const data = await gql(`{ exams { id specialtyId title description } }`);
        if (!data.exams.length) {
            grid.innerHTML = '<div class="empty">Synag yok</div>';
            return;
        }
        grid.innerHTML = data.exams.map(e => `
            <div class="card" onclick="showSubjects(${e.id})">
                <h3>${e.title}</h3>
                <p>${e.description || ''}</p>
                <span class="badge">Dersleri gormek →</span>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Hunar basylanda sol hunarin synaglaryny gorkez
async function showExams(specialtyId) {
    const grid = document.getElementById('exam-grid');
    try {
        const data = await gql(`{ examsBySpecialty(specialtyId: ${specialtyId}) { id specialtyId title description } }`);
        if (!data.examsBySpecialty.length) {
            grid.innerHTML = '<div class="empty">Bu hunarde synag yok</div>';
        } else {
            grid.innerHTML = data.examsBySpecialty.map(e => `
                <div class="card" onclick="showSubjects(${e.id})">
                    <h3>${e.title}</h3>
                    <p>${e.description || ''}</p>
                    <span class="badge">Dersleri gormek →</span>
                </div>
            `).join('');
            // Hünär saýlananda degişli derslerem bile getirilýär
            const subj = document.getElementById('subject-grid');
            try {
                const subData = await gql(`{ subjectsBySpecialty(specialtyId: ${specialtyId}) { id examId name maxScore } }`);
                if (subData.subjectsBySpecialty.length) {
                    subj.innerHTML = subData.subjectsBySpecialty.map(s => `
                        <div class="card">
                            <h3>${s.name}</h3>
                            <p>Max bal: ${s.maxScore}</p>
                            <div class="subject-actions">
                                <span class="badge" onclick="showQuestions(${s.id})">Sowalnama →</span>
                                <span class="badge" onclick="loadLectures(${s.id})">Leksiýalar →</span>
                            </div>
                        </div>
                    `).join('');
                }
            } catch (e) { /* dersler yalnyszlykda asyl sanawy sakla */ }
        }
        switchTab('exams');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// ---------- DERSLER ----------
async function loadSubjects() {
    const grid = document.getElementById('subject-grid');
    try {
        const data = await gql(`{ subjects { id examId name maxScore } }`);
        if (!data.subjects.length) {
            grid.innerHTML = '<div class="empty">Ders yok</div>';
            return;
        }
grid.innerHTML = data.subjects.map(s => `
            <div class="card">
                <h3>${s.name}</h3>
                <p>Max bal: ${s.maxScore}</p>
                <div class="subject-actions">
                    <span class="badge" onclick="showQuestions(${s.id})">Sowalnama →</span>
                    <span class="badge" onclick="loadLectures(${s.id})">Leksiýalar →</span>
                </div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Synag basylanda sol synagyn derslerini gorkez
async function showSubjects(examId) {
    const grid = document.getElementById('subject-grid');
    try {
        const data = await gql(`{ subjectsByExam(examId: ${examId}) { id examId name maxScore } }`);
        if (!data.subjectsByExam.length) {
            grid.innerHTML = '<div class="empty">Bu synagda ders yok</div>';
        } else {
grid.innerHTML = data.subjectsByExam.map(s => `
                <div class="card">
                    <h3>${s.name}</h3>
                    <p>Max bal: ${s.maxScore}</p>
                    <div class="subject-actions">
                        <span class="badge" onclick="showQuestions(${s.id})">Sowalnama →</span>
                        <span class="badge" onclick="loadLectures(${s.id})">Leksiýalar →</span>
                    </div>
                </div>
            `).join('');
        }
        switchTab('subjects');
    } catch (e) {
        grid.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// ---------- SORAGLAR ----------
async function showQuestions(subjectId) {
    const area = document.getElementById('question-area');
    try {
        const data = await gql(`{ questionsBySubject(subjectId: ${subjectId}) { id text optionA optionB optionC optionD } }`);
        if (!data.questionsBySubject.length) {
            area.innerHTML = '<div class="empty">Bu dersde sorag yok</div>';
        } else {
            area.innerHTML = data.questionsBySubject.map((q, i) => `
                <div class="question-block">
                    <h3>${i + 1}. ${q.text}</h3>
                    <label class="option"><input type="radio" name="q${q.id}" value="A"> A) ${q.optionA}</label>
                    <label class="option"><input type="radio" name="q${q.id}" value="B"> B) ${q.optionB}</label>
                    <label class="option"><input type="radio" name="q${q.id}" value="C"> C) ${q.optionC}</label>
                    <label class="option"><input type="radio" name="q${q.id}" value="D"> D) ${q.optionD}</label>
                </div>
            `).join('');
            area.innerHTML += `<button class="submit-btn" onclick="submitAnswers(${subjectId})">Jogablary ugrat</button>`;
            area.innerHTML += `<div id="result"></div>`;
        }
        switchTab('questions');
    } catch (e) {
        area.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Jogablary ugrat
async function submitAnswers(subjectId) {
    const questions = document.querySelectorAll('.question-block');
    const answers = {};
    questions.forEach(q => {
        const radio = q.querySelector('input[type="radio"]:checked');
        const qid = radio ? radio.name.replace('q', '') : null;
        if (radio) answers[qid] = radio.value;
    });

    // User id (superuser Nepes id=1)
    const userId = 1;

try {
        const data = await gql(`
            mutation ($userId: Int!, $subjectId: Int!, $answers: JSON!) {
                submitAnswer(userId: $userId, subjectId: $subjectId, answers: $answers) {
                    correctCount totalCount score rating
                    details { questionId text userAnswer correctAnswer isCorrect }
                }
            }
        `, { userId, subjectId, answers });
        const r = data.submitAnswer;
        let detailHtml = '';
        if (r.details && r.details.length) {
            detailHtml = r.details.map((d, i) => `
                <div class="answer-detail ${d.isCorrect ? 'correct' : 'wrong'}">
                    ${i + 1}. ${d.text}<br>
                    <span class="u-answer">Siziň jogabyňyz: ${d.userAnswer || '—'}</span>
                    ${!d.isCorrect ? `<span class="c-answer"> Dogry jogap: ${d.correctAnswer}</span>` : ''}
                </div>
            `).join('');
        }
        document.getElementById('result').innerHTML = `
            <div class="result-box">
                Dogry: ${r.correctCount} / ${r.totalCount}<br>
                Bal: ${r.score} / 100<br>
                Reyting: ${r.rating}
            </div>
            ${detailHtml}
        `;
        loadRating();
    } catch (e) {
        document.getElementById('result').innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// ---------- REYTING ----------
async function loadRating() {
    const tbody = document.querySelector('#rating-table tbody');
    try {
        const data = await gql(`{ rating { rank userId username rating discount } }`);
        if (!data.rating.length) {
            tbody.innerHTML = '<tr><td colspan="4">Reyting yok</td></tr>';
            return;
        }
        tbody.innerHTML = data.rating.map(r => `
            <tr>
                <td class="rank-${r.rank <= 3 ? r.rank : ''}">${r.rank}</td>
                <td>${r.username}</td>
                <td>${r.rating}</td>
                <td>${r.discount ? `<span class="discount">${r.discount}</span>` : '—'}</td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="4">Yalnys: ${e.message}</td></tr>`;
    }
}

// ---------- LEKSIÝALAR ----------
async function loadLectures(subjectId) {
    const area = document.getElementById('lecture-area');
    try {
        const data = await gql(`{ topicsBySubject(subjectId: ${subjectId}) { id title description } }`);
        if (!data.topicsBySubject.length) {
            area.innerHTML = '<div class="empty">Bu dersde tema yok</div>';
        } else {
            area.innerHTML = data.topicsBySubject.map(t => `
                <div class="card lecture-topic-card" onclick="showTopic(${t.id}, ${subjectId})">
                    <h3>📘 ${t.title}</h3>
                    <p>${t.description || ''}</p>
                    <span class="badge">Leksiýalary gör →</span>
                </div>
            `).join('');
        }
        switchTab('lectures');
    } catch (e) {
        area.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Temany basanda leksiýalary görkez
async function showTopic(topicId, subjectId) {
    const area = document.getElementById('lecture-area');
    try {
        const data = await gql(`{ lecturesByTopic(topicId: ${topicId}) { id title contentType contentText imageUrl pdfUrl audioUrl videoUrl } }`);
        if (!data.lecturesByTopic.length) {
            area.innerHTML = '<div class="empty">Bu temada leksiýa yok</div>';
        } else {
            area.innerHTML = data.lecturesByTopic.map(l => renderLecture(l)).join('');
            area.innerHTML += `<button class="submit-btn" onclick="loadLectures(${subjectId})" style="margin-top:20px">← Temalar yza</button>`;
        }
    } catch (e) {
        area.innerHTML = `<div class="empty">Yalnys: ${e.message}</div>`;
    }
}

// Leksiýany formatyna görä render et
function renderLecture(l) {
    let content = '';
    if (l.contentText) {
        content += `<div class="lecture-content">${l.contentText}</div>`;
    }
    if (l.imageUrl) {
        content += `<img src="${l.imageUrl}" alt="${l.title}" class="lecture-image">`;
    }
    if (l.pdfUrl) {
        content += `<a class="badge" href="${l.pdfUrl}" target="_blank">📄 PDF aç</a>`;
    }
    if (l.audioUrl) {
        content += `<audio controls src="${l.audioUrl}" class="lecture-audio"></audio>`;
    }
    if (l.videoUrl) {
        content += `<video controls src="${l.videoUrl}" class="lecture-video"></video>`;
    }
    if (!content) {
        content = '<div class="empty">Bu leksiýada mazmun yok</div>';
    }
    const typeLabel = {
        text: '📝 Tekst', formula: '🧮 Formula', image: '🖼️ Surat',
        audio: '🎵 Saz', video: '🎬 Wideo', pdf: '📄 PDF'
    }[l.contentType] || l.contentType;
    return ` 
        <div class="card lecture-card">
            <h3>${typeLabel} — ${l.title}</h3>
            ${content}
        </div>
    `;
}

// Tab geciriji komekci
function switchTab(tabId) {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const btn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);
    if (btn) btn.classList.add('active');
    const tab = document.getElementById(tabId);
    if (tab) tab.classList.add('active');
}
