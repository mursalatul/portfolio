from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import (
    Profile, Skill, Project, Experience,
    Education, Achievement, Publication, Leadership, WebsiteSetting
)



def index(request):
    profile = Profile.objects.first()
    skills_by_category = {}
    for skill in Skill.objects.all():
        skills_by_category.setdefault(skill.category, []).append(skill)

    achievements_qs = Achievement.objects.all()
    all_projects_qs = Project.objects.all()
    featured_projects = all_projects_qs.filter(featured=True)[:6]
    publications_qs = Publication.objects.all()

    context = {
        'profile': profile,
        'skills_by_category': skills_by_category,
        'projects': featured_projects,
        'all_projects': all_projects_qs,
        'experiences': Experience.objects.all(),
        'education': Education.objects.all(),
        'achievements': achievements_qs,
        'publications': publications_qs,
        'leadership': Leadership.objects.all(),
        # Auto-computed counts
        'achievements_count': achievements_qs.count(),
        'projects_count': all_projects_qs.count(),
        'publications_count': publications_qs.count(),
        'has_more_projects': all_projects_qs.count() > featured_projects.count(),
        'settings': WebsiteSetting.objects.first(),
    }
    return render(request, 'core/index.html', context)


def contact_submit(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)

    name    = request.POST.get('name', '').strip()
    email   = request.POST.get('email', '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    if not all([name, email, subject, message]):
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

    # Dhaka time
    now = timezone.localtime(timezone.now())
    time_str = now.strftime('%A, %d %B %Y  •  %I:%M %p (Dhaka Time)')

    body = f"""\
========================================
  NEW CONTACT FORM SUBMISSION
========================================

  Received  :  {time_str}

----------------------------------------
  From      :  {name}
  Email     :  {email}
  Subject   :  {subject}
----------------------------------------

  Message:

{message}

----------------------------------------
This email was sent from the contact form on your portfolio.
Reply directly to {email} to respond.
"""

    try:
        send_mail(
            subject=f'[Portfolio Contact] {subject}',
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
