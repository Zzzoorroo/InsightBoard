"""Models for uploaded file metadata."""
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()

class UploadedFile(models.Model):
    """
    REQ-01: Stores the raw Excel/CSV file uploaded by the user.
    """
    file = models.FileField(
        upload_to='raw_data/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata to track processing status (REQ-02)
    filename = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(help_text="Size in bytes", null=True, blank=True)
    is_processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-extract filename and size before saving
        if self.file:
            self.filename = os.path.basename(self.file.name)
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.filename} ({self.uploaded_by.username})"