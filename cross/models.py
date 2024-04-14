from django.db import models

from django.contrib.auth.models import User

# Create your models here.

# if any changes are made, run "python manage.py makemigrations cross"
# run "python manage.py sqlmigrate crjoss 0001" to see the sql query it would make
# run "python manage.py check" to check for problems without making any changes
class UserData (models.Model):
    # username = models.CharField(max_length=200, primary_key=True)
    # password = models.CharField(max_length=200)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default="")

    current_cross = models.CharField(max_length=244, default="")

    crosses_started = models.IntegerField(default=0)
    crosses_completed = models.IntegerField(default=0)
    def __str__(self)->str:
        return self.username

# class FriendsList (models.Model):
#     user1 = models.ForeignKey(UserData, related_name="user1", on_delete=models.CASCADE)
#     user2 = models.ForeignKey(UserData, related_name="user2", on_delete=models.CASCADE)

# class FriendRequests(models.Model):
#     sender = models.ForeignKey(UserData, related_name="sender", on_delete=models.CASCADE)
#     receiver = models.ForeignKey(UserData, related_name="receiver", on_delete=models.CASCADE)