"""
SheShield AI — Core App Models
All data models for the platform.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User extending Django's AbstractUser."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    safety_score = models.IntegerField(default=85)
    is_location_sharing = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def profile_completion(self):
        fields = [self.first_name, self.last_name, self.phone,
                  self.bio, self.city, self.profile_photo]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    @property
    def dob(self):
        return self.date_of_birth

    @dob.setter
    def dob(self, value):
        self.date_of_birth = value


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year_start = models.IntegerField()
    year_end = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.degree} — {self.institution}"


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    proficiency = models.IntegerField(default=50)  # 0-100

    def __str__(self):
        return self.name


class EmergencyContact(models.Model):
    """Emergency contacts for SOS feature."""
    RELATION_CHOICES = [
        ('mother', 'Mother'), ('father', 'Father'), ('sister', 'Sister'),
        ('brother', 'Brother'), ('friend', 'Friend'), ('spouse', 'Spouse'), ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default='other')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.relation})"


class SOSAlert(models.Model):
    """SOS alert triggered by user."""
    STATUS_CHOICES = [('active', 'Active'), ('resolved', 'Resolved'), ('false_alarm', 'False Alarm')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"SOS by {self.user} at {self.created_at:%d %b %Y %H:%M}"

    @property
    def duration(self):
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return f"{int(delta.total_seconds() // 60)} min"
        return None


class Mentor(models.Model):
    """Mentor profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    experience = models.IntegerField(default=0)
    bio = models.TextField()
    fee = models.CharField(max_length=50, default='Free')
    is_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    review_count = models.IntegerField(default=0)
    sessions_count = models.IntegerField(default=0)
    response_rate = models.IntegerField(default=100)
    photo = models.ImageField(upload_to='mentors/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.title}"

    @property
    def name(self):
        return self.user.get_full_name() or self.user.username


class MentorSkill(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)


class MentorSession(models.Model):
    """Booked sessions between user and mentor."""
    SESSION_TYPE_CHOICES = [('video', 'Video Call'), ('chat', 'Chat')]
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, default='video')
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.mentor.user.get_full_name()} on {self.date}"


class MentorReview(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Job(models.Model):
    """Job listings."""
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'), ('part-time', 'Part-time'),
        ('remote', 'Remote'), ('contract', 'Contract'), ('internship', 'Internship'),
    ]
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full-time')
    experience = models.CharField(max_length=50, blank=True)
    is_women_friendly = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    company_logo = models.CharField(max_length=10, default='💼')
    deadline = models.DateField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    applicants = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} @ {self.company}"


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [('applied', 'Applied'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    class Meta:
        unique_together = ('user', 'job')


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')


class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    deadline = models.DateField()
    icon = models.CharField(max_length=10, default='🎓')
    apply_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    CATEGORY_CHOICES = [('legal', 'Legal'), ('health', 'Health'), ('pdf', 'PDF'), ('video', 'Video'), ('other', 'Other')]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


class Notification(models.Model):
    CATEGORY_CHOICES = [('safety', 'Safety'), ('career', 'Career'), ('system', 'System')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system')
    icon = models.CharField(max_length=10, default='🔔')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.user}] {self.title}"


class CareerChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_chats')
    title = models.CharField(max_length=200, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.title}"


class CareerMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('ai', 'AI')]
    chat = models.ForeignKey(CareerChat, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class CareerRoadmap(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='roadmap')
    title = models.CharField(max_length=200)
    goal = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.title}"

    @property
    def overall_pct(self):
        steps = self.steps.all()
        if not steps:
            return 0
        completed = steps.filter(status='completed').count()
        return int((completed / steps.count()) * 100)


class RoadmapStep(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')]
    roadmap = models.ForeignKey(CareerRoadmap, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)
    resource_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class LiveLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    location_name = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} at {self.latitude}, {self.longitude}"


class VerifiedService(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    icon = models.CharField(max_length=10, default='🚑')
    availability = models.CharField(max_length=50, default='24x7')

    def __str__(self):
        return self.name


class SafeRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='safe_routes')
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    travel_mode = models.CharField(max_length=20, default='walk')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.start_location} -> {self.end_location}"
