from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.university import University
from app.infrastructure.database.models.faculty import Faculty
from app.infrastructure.database.models.specialty import Specialty, SpecialtyRegionAdmission
from app.infrastructure.database.models.region import Region
from app.infrastructure.database.models.exam import EntranceExam, timeExam
from app.infrastructure.database.models.subject import Subject
from app.infrastructure.database.models.school import School, SchoolClass
from app.infrastructure.database.models.tutor import OnlineTutor
from app.infrastructure.database.models.videolesson import VideoLesson
from app.infrastructure.database.models.lecture import Lecture, LectureTopic, LectureG, SchoolSubjectPDF
from app.infrastructure.database.models.question import Question
from app.infrastructure.database.models.result import ExamResult
from app.infrastructure.database.models.subscription import Subscription, SubscriptionPlanPrice
from app.infrastructure.database.models.payment import Payment

__all__ = [
    'User',
    'University',
    'Faculty',
    'Specialty',
    'SpecialtyRegionAdmission',
    'Region',
    'EntranceExam',
    'Subject',
    'School',
    'SchoolClass',
    'Lecture',
    'LectureTopic',
    'LectureG',
    'SchoolSubjectPDF',
    'Question',
    'ExamResult',
    'Subscription',
    'SubscriptionPlanPrice',
    'Payment',
    'OnlineTutor',
    'VideoLesson',
]
