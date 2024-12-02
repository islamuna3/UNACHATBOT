from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField


class FixedQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    question = models.TextField(max_length=512)  # Limit length
    answer = models.TextField(max_length=2048)   # Limit length
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]  # Display first 50 characters


class QuestionAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(max_length=512)
    answer = models.TextField(max_length=2048)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    fixed_question = models.ForeignKey(FixedQuestions, on_delete=models.CASCADE, null=True, blank=True)
    embedding = ArrayField(models.FloatField(), blank=True, null=True)  # ??? ?????? Embedding ?????? ?? ??????? ???????

    def delete(self, *args, **kwargs):
        if self.fixed_question:
            raise Exception("This question cannot be deleted directly. Please delete it from the fixed questions.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.question[:50]  # Display first 50 characters

# class QuestionAnswer(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     question = models.TextField(max_length=512)
#     answer_type = models.CharField(max_length=10, choices=[('single', '????? ?????'), ('multiple', '?????? ??????')], default='single')
#     answers = models.TextField(max_length=4096)
#     count = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     fixed_question = models.ForeignKey(FixedQuestions, on_delete=models.CASCADE, null=True, blank=True)
#     embedding = ArrayField(models.FloatField(), blank=True, null=True)
#
#     def get_answers_list(self):
#         # ????? ???????? ??? ????? ????? ??? ???????
#         return self.answers.split('\n') if self.answer_type == 'multiple' else [self.answers]
#
#     def delete(self, *args, **kwargs):
#         if self.fixed_question:
#             raise Exception("This question cannot be deleted directly. Please delete it from the fixed questions.")
#         super().delete(*args, **kwargs)
#
#     def __str__(self):
#         return self.question[:50]


class UnansweredQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(max_length=512)  # Limit length

    def __str__(self):
        return self.question[:50]  # Display first 50 characters
