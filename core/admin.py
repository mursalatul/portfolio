from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile, Skill, Project, Experience,
    Education, Achievement, Publication, Leadership
)

# Customize admin site header
admin.site.site_header = '🚀 Pallob Portfolio Admin'
admin.site.site_title = 'Portfolio Admin'
admin.site.index_title = 'Portfolio Management'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'tagline', 'roles', 'about_text', 'profile_photo')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'github_url', 'linkedin_url', 'resume_file')
        }),
        ('Stats', {
            'fields': ('cgpa', 'years_experience', 'achievements_count', 'projects_count')
        }),
    )

    def profile_photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" style="width:80px;border-radius:50%"/>', obj.profile_photo.url)
        return '-'
    profile_photo_preview.short_description = 'Photo Preview'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon', 'order')
    list_editable = ('order',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('category', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'tech_tags', 'featured', 'order')
    list_editable = ('featured', 'order')
    search_fields = ('title', 'description')
    list_filter = ('featured',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'start_date', 'end_date', 'is_current', 'order')
    list_editable = ('order',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'cgpa', 'start_year', 'end_year', 'order')
    list_editable = ('order',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'rank', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'event')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'status', 'journal', 'year', 'order')
    list_editable = ('order',)
    list_filter = ('status',)

    def short_title(self, obj):
        return obj.title[:70] + '...' if len(obj.title) > 70 else obj.title
    short_title.short_description = 'Title'


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ('role', 'org', 'start_date', 'end_date', 'order')
    list_editable = ('order',)
