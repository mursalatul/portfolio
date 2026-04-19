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

    context = {
        'profile': profile,
        'skills_by_category': skills_by_category,
        'projects': Project.objects.all(),
        'experiences': Experience.objects.all(),
        'education': Education.objects.all(),
        'achievements': Achievement.objects.all(),
        'publications': Publication.objects.all(),
        'leadership': Leadership.objects.all(),
    }
    return render(request, 'core/index.html', context)
