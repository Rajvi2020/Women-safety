from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Education, Skill, EmergencyContact, SOSAlert, Mentor,
    MentorSkill, MentorSession, MentorReview, Job, JobApplication, SavedJob,
    Scholarship, Resource, FAQ, Notification, CareerChat, CareerMessage,
    CareerRoadmap, RoadmapStep, LiveLocation, VerifiedService, SafeRoute
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'safety_score', 'bio', 'phone', 'city', 'profile_photo', 'resume')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'safety_score', 'bio', 'phone', 'city', 'profile_photo', 'resume')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'safety_score', 'is_staff']
    list_filter = ['role', 'safety_score', 'is_staff', 'is_superuser']

admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(EmergencyContact)
admin.site.register(SOSAlert)
admin.site.register(Mentor)
admin.site.register(MentorSkill)
admin.site.register(MentorSession)
admin.site.register(MentorReview)
admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(SavedJob)
admin.site.register(Scholarship)
admin.site.register(Resource)
admin.site.register(FAQ)
admin.site.register(Notification)
admin.site.register(CareerChat)
admin.site.register(CareerMessage)
admin.site.register(CareerRoadmap)
admin.site.register(RoadmapStep)
admin.site.register(LiveLocation)
admin.site.register(VerifiedService)
admin.site.register(SafeRoute)
