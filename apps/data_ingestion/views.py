"""Views for handling uploads and preprocessing."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
from .models import UploadedFile

@login_required
def upload_file_view(request):
    """
    Handles file upload.
    On GET: Renders the upload form.
    On POST: Validates and saves the file to media/raw_data.
    """
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create instance but don't save to DB yet
            instance = form.save(commit=False)
            # Assign the currently logged-in user
            instance.uploaded_by = request.user 
            instance.save()
            return redirect('upload_success') # We will create this URL next
    else:
        form = FileUploadForm()
    
    return render(request, 'data_ingestion/upload.html', {'form': form})

@login_required
def upload_success_view(request):
    files = UploadedFile.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'data_ingestion/success.html', {'files': files})