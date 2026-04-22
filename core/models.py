from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=200, default='Md Mursalatul Islam Pallob')
    tagline = models.CharField(max_length=300, default='Software Engineer & AI/ML Researcher')
    roles = models.CharField(
        max_length=500,
        default='Software Developer,AI/ML Researcher,Competitive Programmer',
        help_text='Comma-separated list of rotating roles for hero typewriter'
    )
    about_text = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    show_email_in_about = models.BooleanField(default=True, verbose_name="Show Email in 'Who Am I'")
    show_email_in_contact = models.BooleanField(default=True, verbose_name="Show Email in 'Contact'")

    phone = models.CharField(max_length=30, blank=True)
    show_phone_in_about = models.BooleanField(default=True, verbose_name="Show Phone in 'Who Am I'")
    show_phone_in_contact = models.BooleanField(default=True, verbose_name="Show Phone in 'Contact'")

    github_url = models.URLField(blank=True)
    show_github_in_about = models.BooleanField(default=True, verbose_name="Show GitHub in 'Who Am I'")
    show_github_in_contact = models.BooleanField(default=True, verbose_name="Show GitHub in 'Contact'")

    linkedin_url = models.URLField(blank=True)
    show_linkedin_in_about = models.BooleanField(default=True, verbose_name="Show LinkedIn in 'Who Am I'")
    show_linkedin_in_contact = models.BooleanField(default=True, verbose_name="Show LinkedIn in 'Contact'")

    facebook_url = models.URLField(blank=True)
    show_facebook_in_about = models.BooleanField(default=True, verbose_name="Show Facebook in 'Who Am I'")
    show_facebook_in_contact = models.BooleanField(default=True, verbose_name="Show Facebook in 'Contact'")
    resume_file = models.FileField(upload_to='resume/', blank=True)
    profile_photo = models.ImageField(upload_to='profile/', blank=True, null=True)
    years_experience = models.PositiveIntegerField(default=3)
    cp_problems_authored = models.PositiveIntegerField(default=0, help_text='Number of CP problems authored (set manually)')
    cp_problems_solved = models.PositiveIntegerField(default=0, help_text='Number of CP problems solved (set manually)')

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profile'

    def __str__(self):
        return self.name

    def get_roles_list(self):
        return [r.strip() for r in self.roles.split(',')]


class HeroBadge(models.Model):
    profile = models.ForeignKey(Profile, related_name='hero_badges', on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    color = models.CharField(max_length=50, default='#10B981', help_text='Hex color or CSS variable')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Languages', 'Languages'),
        ('Frameworks', 'Frameworks'),
        ('Tools', 'Developer Tools'),
        ('Libraries', 'Libraries'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=100, blank=True, help_text='Devicon class — see devicon.dev. E.g. devicon-python-plain. Note: DRF has no icon, use devicon-django-plain instead.')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f'{self.name} ({self.category})'


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tech_tags = models.CharField(max_length=500, help_text='Comma-separated tags')
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-featured']

    def __str__(self):
        return self.title

    def get_tech_list(self):
        return [t.strip() for t in self.tech_tags.split(',')]


class Experience(models.Model):
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(help_text='Bullet points separated by newlines')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.role} @ {self.company}'

    def get_bullets(self):
        return [b.strip() for b in self.description.split('\n') if b.strip()]


class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=300)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.degree} @ {self.institution}'


class Achievement(models.Model):
    title = models.CharField(max_length=300)
    event = models.CharField(max_length=300, blank=True)
    year = models.CharField(max_length=10, blank=True)
    rank = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Publication(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('working', 'Working On'),
        ('published', 'Published'),
        ('preprint', 'Preprint'),
    ]
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    journal = models.CharField(max_length=300, blank=True)
    year = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title[:80]


class Leadership(models.Model):
    org = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, blank=True)
    bullets = models.TextField(help_text='Activities separated by newlines')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.role} @ {self.org}'

class WebsiteSetting(models.Model):
    FONT_CHOICES = [
        ('normal', 'Normal'),
        ('josefin', 'Josefin Sans'),
        ('teko', 'Teko'),
    ]
    website_font = models.CharField(
        max_length=50, 
        choices=FONT_CHOICES, 
        default='josefin', 
        verbose_name="Website Font"
    )

    class Meta:
        verbose_name = 'Website Setting'
        verbose_name_plural = 'Website Settings'

    def __str__(self):
        return "Website Settings"
