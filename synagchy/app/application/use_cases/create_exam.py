class CreateExamUseCase:

    def __init__(self, exam_repository):
        self.exam_repository = exam_repository


    def execute(self, data):

        exam = Exam(
            title=data["title"]
        )

        return self.exam_repository.save(exam)
