
from datetime import datetime
from email.policy import default
from django.db import models
from tgbot.models import User
from tgbot import consts
from exam.models import Question


NOT_FINISHED = "not_finished"
IN_PROGRESS = "in_progress"
FINISHED = "finished"


CHALLENGE_STATUS = (
    (consts.PUBLIC, "public"),
    (consts.PRIVATE, "private"),

)

USER_TASK_STATUS = (
    (NOT_FINISHED, "not_finished"),
    (IN_PROGRESS, "in_progress"),
    (FINISHED, "finished"),
)


class Challenge(models.Model):
    stage = models.CharField(max_length=16, null=True, blank=True)
    questions = models.ManyToManyField(Question)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challengelar"

    def create_user_challenge(self, telegram_id, challenge):
        user = User.objects.get(user_id=telegram_id)
        user_challenge = UserChallenge.objects.create(
            user=user, challenge=challenge)
        user_challenge.users.add(user)
        user_challenge.questions.set(self.questions.all(
        ).order_by("?")[:10])
        return user_challenge


class UserChallenge(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner")
    opponent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="opponent", null=True, blank=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="user_challenges")
    is_active = models.BooleanField(default=True)
    questions = models.ManyToManyField(Question)

    user_score = models.IntegerField(default=0)
    opponent_score = models.IntegerField(default=0)

    user_started_at = models.DateTimeField(null=True)
    user_finished_at = models.DateTimeField(null=True)
    user_duration = models.CharField(max_length = 256, null=True)
    
    opponent_started_at = models.DateTimeField(null=True)
    opponent_finished_at = models.DateTimeField(null=True)
    opponent_duration = models.CharField(max_length = 256, null=True)
    

    is_user_finished = models.BooleanField(default=False)
    is_opponent_finished = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def user_duration(self):
        difference = self.user_finished_at-self.user_started_at
        difference = difference.total_seconds()
        difference = int(difference)
        

        return difference
    
    def opponent_duration(self):
        difference = self.opponent_finished_at-self.opponent_started_at 
        difference = difference.total_seconds()
        difference = int(difference)
        
        # if difference//60==0:
        #     minutes = 0
        #     seconds = difference
        #     self.opponent_duration = f"{difference} sekund"
        # elif difference//60>0:
        #     minutes = difference//60
        #     seconds = difference%60
        #     self.opponent_duration = f"{minutes} daqiqayu {seconds} sekund"
        
        
          
        return difference
        

    def update_score(self, type):
        user_challenge = UserChallenge.objects.get(id=self.id)

        if type == 'user':

            score = UserChallengeAnswer.objects.filter(
                is_correct=True, user_challenge=self, user=self.user).count()
            user_challenge.user_score = int(score)
            user_challenge.save()
        elif type == "opponent":
            score = UserChallengeAnswer.objects.filter(
                is_correct=True, user_challenge=self, user=self.opponent).count()
            user_challenge.opponent_score = int(score)
            user_challenge.save()

        # print(f"score-----{score}")

        return score

    def create_user_answers(self):
        challenge_answers_for_user = []
        for question in self.questions.all().order_by("?"):
            challenge_answers_for_user.append(UserChallengeAnswer(
                user_challenge=self, question=question, user=self.user))

        UserChallengeAnswer.objects.bulk_create(challenge_answers_for_user)

    def create_opponent_answers(self):
        challenge_answers_for_opponent = []

        for question in self.questions.all().order_by("?"):
            challenge_answers_for_opponent.append(UserChallengeAnswer(
                user_challenge=self, question=question, user = self.opponent))
            
            
        UserChallengeAnswer.objects.bulk_create(challenge_answers_for_opponent)
    
    
    def last_unanswered_question(self,user):
        user_challenge_answer = self.answer.all().exclude(answered=True).filter(user = user).first()
        return user_challenge_answer.question if user_challenge_answer else None

    def last_unanswered(self,user):
        user_challenge_answer = self.answer.all().exclude(answered=True).filter(user=user).first()
        return user_challenge_answer


class UserChallengeAnswer(models.Model):
    user_challenge = models.ForeignKey(
        UserChallenge, on_delete=models.CASCADE, related_name="answer")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_ids = models.CharField(max_length=255, null=True)
    answered = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    
class Rate(models.Model):
    stars_count = models.IntegerField(default=0)
    old_stars_count = models.IntegerField(default=0)    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE, null=True, blank = True)
    
    
        
