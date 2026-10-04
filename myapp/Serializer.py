from rest_framework import serializers
from .models import FileUpload


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'file', 'uploaded_at']

    def validate_file(self, value):
        # Example: Limit file size to 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size should not exceed 5MB.")

        # Example: Allow only specific file types
        if not value.name.endswith(('.png', '.jpg', '.pdf')):
            raise serializers.ValidationError("Only .png, .jpg, or .pdf files are allowed.")

        return value
