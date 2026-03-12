from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Review(models.Model):
    # Star rating labels set cheyyunnu
    class RatingChoices(models.IntegerChoices):
        ONE_STAR = 1, 'Bad'
        TWO_STARS = 2, 'Below Average'
        THREE_STARS = 3, 'Average'
        FOUR_STARS = 4, 'Good'
        FIVE_STARS = 5, 'Excellent'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        choices=RatingChoices.choices,
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=True) # Admin control
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} Stars ({self.get_rating_display()})"