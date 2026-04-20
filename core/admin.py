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
        ('Contact & Visibility', {
            'fields': (
                ('email', 'show_email_in_about', 'show_email_in_contact'),
                ('phone', 'show_phone_in_about', 'show_phone_in_contact'),
                ('github_url', 'show_github_in_about', 'show_github_in_contact'),
                ('linkedin_url', 'show_linkedin_in_about', 'show_linkedin_in_contact'),
                ('facebook_url', 'show_facebook_in_about', 'show_facebook_in_contact'),
                'resume_file'
            )
        }),
        ('Stats', {
            'fields': ('years_experience', 'cp_problems_authored', 'cp_problems_solved')
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
    list_display = ('title', 'featured_badge', 'tech_tags', 'date', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description', 'tech_tags')
    list_filter = ('featured',)
    ordering = ('order',)

    def featured_badge(self, obj):
        featured_count = Project.objects.filter(featured=True).count()
        if obj.featured:
            return format_html(
                '<span style="background:#2563eb;color:white;padding:2px 8px;'
                'border-radius:12px;font-size:0.75rem;">⭐ Featured ({}/6)</span>',
                featured_count
            )
        return format_html('<span style="color:#888;">—</span>')
    featured_badge.short_description = 'Featured (max 6)'
    featured_badge.admin_order_field = 'featured'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        featured_count = Project.objects.filter(featured=True).count()
        if featured_count > 6:
            self.message_user(
                request,
                f'⚠️ Warning: {featured_count} projects are marked as Featured. '
                f'Only the first 6 (by order) will appear on the main page. '
                f'Please update the "order" field or unfeatured some projects.',
                level='warning'
            )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'start_date', 'end_date', 'is_current', 'order')
    list_editable = ('order',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'start_year', 'end_year', 'order')
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
