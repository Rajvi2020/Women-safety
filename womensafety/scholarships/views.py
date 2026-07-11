from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Scholarship

@login_required
def scholarship_list_view(request):
    scholarships = Scholarship.objects.filter(is_active=True)
    return render(request, 'scholarships/scholarship_list.html', {'scholarships': scholarships})


@login_required
def scholarship_detail_view(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    if scholarship.apply_url:
        return redirect(scholarship.apply_url)
    return redirect('scholarships')
