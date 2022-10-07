
from django.db import models
from tgbot.models import User
from tgbot import consts



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
    title = models.CharField(max_length=200, verbose_name="Challenge Nomi")
    content = models.TextField(max_length=4096, null=True)   
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challengelar"
        
    
    def create_user_challenge(self, telegram_id, challenge, status=consts.PUBLIC):
        # super().create_user_challenge(self, telegram_id, status=PUBLIC)
        user_challenge = UserChallenge.objects.create(user=User.objects.get(user_id=telegram_id), challenge = challenge, status=status)           
        user_challenge.users.add(User.objects.get(user_id = telegram_id))
        return user_challenge
    
    


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")    
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="user_challenges")
    is_active = models.BooleanField(default=False) 
    status = models.CharField(max_length=15, choices=CHALLENGE_STATUS, default=consts.PUBLIC) # public hammaga , private ma'lum userlarga
    
    started_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def create_task(self,challenge_id, telegram_id):
        task = Task.objects.create(user = User.objects.get(user_id = telegram_id) ,user_challenge = UserChallenge.objects.get(id = challenge_id))
        return task
    
    
        
    
    
        

    
         

        
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    content = models.TextField(max_length=4096, null=True, blank=True)
    
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE, related_name="tasks")
    
    # start_time 
    # end_time
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def add_title(self, title):
        self.title =  title
        
    def add_content(self, content):
        self.title =  content
        
    
    
    def create_user_task(self):
        for user in self.user_challenge.users.all():
            user_task = UserTask.objects.filter(task=self).filter(user=user).count()
            if user_task==0:
                UserTask.objects.create(task = self, user=user)
    
    def save(self, *args, **kwargs):        
        super(Task, self).save(*args, **kwargs)
        
    def update(self, *args, **kwargs):
        super(Task,self).update(*args, **kwargs)
        
class UserTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="user_tasks")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=USER_TASK_STATUS, default=NOT_FINISHED) 
    
    def create_progress(self):
        Progress.objects.create(user_task = self )
        return self
    
    
    def create_rate(self, user):
        Rate.objects.create(user = user, user_challenge = self.task.user_challenge)
        
    
    def increase_stars(self, user):
        rate = Rate.objects.filter(user=user).get(user_challenge=self.task.user_challenge)
        rate.stars_count+=1
        rate.old_stars_count+=1
        rate.save()
        
    def decrease_stars(self, user):
        rate = Rate.objects.filter(user=user).get(user_challenge=self.task.user_challenge)
        rate.stars_count=0
        rate.save()
        
    
    
    
class Progress(models.Model):
    challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE, related_name="challenge_progress")
    user_task = models.ForeignKey(UserTask, on_delete=models.CASCADE, related_name="task_progresses")   
    image = models.CharField(max_length=4096, null=True)
    content = models.TextField(max_length=4096, null=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def add_image(self):
        pass
    
    def add_content(self):
        pass
    
    def save(self, *args, **kwargs):        
        super(Progress, self).save(*args, **kwargs)
        
    def update(self, *args, **kwargs):
        super(Progress,self).update(*args, **kwargs)
    

        
class Rate(models.Model):
    stars_count = models.IntegerField(default=0)
    old_stars_count = models.IntegerField(default=0)    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE, null=True, blank = True)
    
    
        
