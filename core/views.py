from django.shortcuts import render
from .models import (
    Profile, Skill, Project, Experience,
    Education, Achievement, Publication, Leadership
)


def index(request):
    profile = Profile.objects.first()
    skills_by_category = {}
    for skill in Skill.objects.all():
        skills_by_category.setdefault(skill.category, []).append(skill)

    achievements_qs = Achievement.objects.all()
    projects_qs = Project.objects.all()
    publications_qs = Publication.objects.all()

    context = {
        'profile': profile,
        'skills_by_category': skills_by_category,
        'projects': projects_qs,
        'experiences': Experience.objects.all(),
        'education': Education.objects.all(),
        'achievements': achievements_qs,
        'publications': publications_qs,
        'leadership': Leadership.objects.all(),
        # Auto-computed counts
        'achievements_count': achievements_qs.count(),
        'projects_count': projects_qs.count(),
        'publications_count': publications_qs.count(),
    }
    return render(request, 'core/index.html', context)
