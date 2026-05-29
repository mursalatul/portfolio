import os
import json
import urllib.request
import urllib.error
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html
from django.views.decorators.http import require_GET, require_POST
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Profile, HeroBadge, Skill, Project, Experience,
    Education, Achievement, Publication, Leadership, WebsiteSetting,
    CurrentlyWorkingOn
)

# ── Admin site branding ───────────────────────────────────────────────────────
admin.site.site_header = '🚀 Pallob Portfolio Admin'
admin.site.site_title  = 'Portfolio Admin'
admin.site.index_title = 'Portfolio Management'


# ── GitHub helpers ────────────────────────────────────────────────────────────

GITHUB_USER = 'mursalatul'


def _github_api(url: str) -> list:
    """Fetch JSON from the GitHub API using the PAT from environment."""
    token = os.environ.get('GITHUB_TOKEN', '')
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def _humanise(name: str) -> str:
    """Convert repo slug to a readable title."""
    return name.replace('-', ' ').replace('_', ' ').title()


def _build_tech_tags(language: str, topics: list) -> str:
    """
    Build a comma-separated tech_tags string from:
      - Primary language reported by GitHub
      - Repository topics (title-cased, deduplicated)
    """
    tags = []
    if language:
        tags.append(language)
    for topic in topics:
        tag = topic.replace('-', ' ').title()
        if tag not in tags:
            tags.append(tag)
    return ','.join(tags)


def _fetch_new_repos():
    """
    Return list of GitHub repo dicts not yet stored in Project.github_url.
    Handles pagination (up to 200 repos).
    """
    existing_urls = set(Project.objects.values_list('github_url', flat=True))

    all_repos = []
    page = 1
    while True:
        # /user/repos returns ALL repos (public + private) for the authenticated owner.
        # /users/{name}/repos only returns public repos.
        url = (
            f'https://api.github.com/user/repos'
            f'?per_page=100&sort=updated&page={page}&visibility=all&affiliation=owner'
        )
        batch = _github_api(url)
        if not batch:
            break
        all_repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    new_repos = []
    for repo in all_repos:
        if repo.get('fork'):          # skip forks
            continue
        if repo['html_url'] in existing_urls:
            continue
        is_private = bool(repo.get('private'))
        language   = repo.get('language') or ''
        topics     = repo.get('topics') or []
        new_repos.append({
            'name':        repo['name'],
            'title':       _humanise(repo['name']),
            'description': repo.get('description') or '',
            'html_url':    repo['html_url'],       # always store for dedup check
            'homepage':    repo.get('homepage') or '',
            'language':    language,
            'topics':      topics,
            'tech_tags':   _build_tech_tags(language, topics),
            'private':     is_private,             # used by UI + import view
            'stars':       repo.get('stargazers_count', 0),
            'forks':       repo.get('forks_count', 0),
        })
    return new_repos


# ── Admin views (registered via get_urls) ────────────────────────────────────

@staff_member_required
def check_github_view(request):
    """GET — return JSON list of new GitHub repos."""
    try:
        repos = _fetch_new_repos()
        return JsonResponse({'repos': repos})
    except urllib.error.HTTPError as exc:
        return JsonResponse({'error': f'GitHub API error {exc.code}: {exc.reason}'}, status=502)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@staff_member_required
def import_github_view(request):
    """POST — create Project objects for selected repos."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body)
        repos   = payload.get('repos', [])
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if not repos:
        return JsonResponse({'error': 'No repos selected'}, status=400)

    existing_urls = set(Project.objects.values_list('github_url', flat=True))
    base_order    = Project.objects.count()
    created_titles = []

    for idx, repo in enumerate(repos):
        github_url  = repo.get('github_url', '')
        is_private  = repo.get('private', False)

        # Dedup guard: use html_url for matching regardless of privacy
        if github_url in existing_urls:
            continue

        Project.objects.create(
            title=_humanise(repo.get('name', 'Untitled')),
            description=repo.get('description', ''),
            tech_tags=repo.get('tech_tags', ''),
            # Private repos: don't expose GitHub link on the public portfolio
            github_url='' if is_private else github_url,
            live_url=repo.get('live_url', ''),
            featured=False,
            order=base_order + idx + 1,
        )
        created_titles.append(_humanise(repo.get('name', 'Untitled')))
        existing_urls.add(github_url)


    return JsonResponse({'created': len(created_titles), 'titles': created_titles})


# ── ProjectAdmin ──────────────────────────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display   = ('title', 'featured_badge', 'tech_tags', 'github_link', 'order')
    list_editable  = ('order',)
    search_fields  = ('title', 'description', 'tech_tags')
    list_filter    = ('featured',)
    ordering       = ('order',)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'check-github/',
                self.admin_site.admin_view(check_github_view),
                name='project_check_github',
            ),
            path(
                'import-github/',
                self.admin_site.admin_view(import_github_view),
                name='project_import_github',
            ),
        ]
        return custom + urls

    # ── list columns ──────────────────────────────────────────────

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

    def github_link(self, obj):
        if obj.github_url:
            return format_html(
                '<a href="{}" target="_blank" style="color:#58a6ff;font-size:12px;">'
                '⧉ GitHub</a>', obj.github_url
            )
        return '—'
    github_link.short_description = 'GitHub'

    # ── save hook ────────────────────────────────────────────────

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


# ── Remaining admins (unchanged) ─────────────────────────────────────────────

class HeroBadgeInline(admin.TabularInline):
    model = HeroBadge
    extra = 3


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [HeroBadgeInline]
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
    list_display  = ('name', 'category', 'icon', 'order')
    list_editable = ('order',)
    list_filter   = ('category',)
    search_fields = ('name',)
    ordering      = ('category', 'order')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display  = ('role', 'company', 'start_date', 'end_date', 'is_current', 'order')
    list_editable = ('order',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display  = ('degree', 'institution', 'start_year', 'end_year', 'order')
    list_editable = ('order',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display  = ('title', 'year', 'rank', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'event')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display  = ('short_title', 'status', 'journal', 'year', 'order')
    list_editable = ('order',)
    list_filter   = ('status',)

    def short_title(self, obj):
        return obj.title[:70] + '...' if len(obj.title) > 70 else obj.title
    short_title.short_description = 'Title'


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display  = ('role', 'org', 'start_date', 'end_date', 'order')
    list_editable = ('order',)


@admin.register(WebsiteSetting)
class WebsiteSettingAdmin(admin.ModelAdmin):
    list_display = ('website_font',)

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


@admin.register(CurrentlyWorkingOn)
class CurrentlyWorkingOnAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'progress', 'is_active', 'order')
    list_editable = ('order', 'is_active')
    list_filter   = ('category', 'is_active')
    search_fields = ('title', 'description')
    ordering      = ('order',)
