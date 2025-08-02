from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.papers.models import Paper

class ChatRoom(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_rooms'
    
    def __str__(self):
        return f"Chat for {self.paper.title}"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_bot_message = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        username = self.user.username if self.user else "Bot"
        return f"{username}: {self.message[:50]}"
