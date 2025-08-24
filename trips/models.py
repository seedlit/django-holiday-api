from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Destination(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    country = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.latitude:.4f}, {self.longitude:.4f})"


class Schedule(models.Model):
    name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name or f"Schedule #{self.pk}"


class ScheduleItem(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="items"
    )
    destination = models.ForeignKey(
        Destination, on_delete=models.PROTECT, related_name="schedule_items"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order_index", "start_date", "id"]
        unique_together = [("schedule", "order_index")]

    def clean(self):
        # Basic date sanity: start <= end
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "end_date must be on or after start_date"}
            )

    def save(self, *args, **kwargs):
        # Ensure model-level validation runs on .save()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.destination.name} [{self.start_date} → {self.end_date}]"
