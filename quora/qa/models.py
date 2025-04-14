from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Custom user model
class ProgramUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)

    def __str__(self):
        return self.username


# Timestamp model
class TimeStamp(models.Model):
    created_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Audit info model
class AuditEnable(TimeStamp):
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        related_name='+',
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


# Question model (unchanged fields)
class Question(AuditEnable):
    question = models.CharField(max_length=255)
    no_of_answers = models.PositiveBigIntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.question

    def update_answer_count(self):
        self.no_of_answers = self.answers.count()
        self.save()


# Answer model
class Answer(AuditEnable):
    answer = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    no_of_likes = models.PositiveBigIntegerField(null=True, blank=True, default=0)
    no_of_dislikes = models.PositiveBigIntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f"Answer to: {self.question}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.question.update_answer_count()