from django import template
from django.utils.safestring import mark_safe

from apps.jobs.cleaning import clean_job_description
from apps.jobs.models import Job

register = template.Library()

_EMPLOYMENT = dict(Job.EMPLOYMENT_CHOICES)
_SOURCE = dict(Job.SOURCE_CHOICES)


@register.filter
def employment_label(value):
    return _EMPLOYMENT.get(value, value or "Not specified")


@register.filter
def source_label(value):
    return _SOURCE.get(value, value or "")


@register.filter
def initials(name):
    if not name:
        return "?"
    parts = [p for p in str(name).split() if p]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@register.simple_tag
def salary_range(job):
    currency = (job.salary_currency or "").strip()
    prefix = f"{currency} " if currency else ""
    if job.salary_min and job.salary_max:
        return f"{prefix}{job.salary_min:,.0f} – {job.salary_max:,.0f}"
    if job.salary_min:
        return f"From {prefix}{job.salary_min:,.0f}"
    if job.salary_max:
        return f"Up to {prefix}{job.salary_max:,.0f}"
    return "Salary not listed"


@register.simple_tag
def query_replace(request, **kwargs):
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            params.pop(key, None)
        else:
            params[key] = value
    return params.urlencode()


@register.filter
def render_description(job_or_content):
    """
    Renders a job description as safe, clean, and professionally styled HTML.
    Supports either a Job model instance or a raw description string.
    If the description is empty or missing, returns an elegant placeholder card.
    """
    if not job_or_content:
        return mark_safe(_render_empty_description())

    source = ""
    app_url = ""
    if hasattr(job_or_content, "description"):
        content = job_or_content.description
        source = getattr(job_or_content, "source", "")
        app_url = getattr(job_or_content, "application_url", "")
    else:
        content = str(job_or_content)

    cleaned = clean_job_description(content, source=source)
    if not cleaned or not cleaned.strip():
        return mark_safe(_render_empty_description(app_url))

    return mark_safe(cleaned)


def _render_empty_description(application_url=""):
    button_html = ""
    if application_url:
        button_html = f'''
        <p style="margin-top:1rem;">
            <a class="btn-secondary" href="{application_url}" target="_blank" rel="noopener noreferrer">
                View role &amp; apply on company site &rarr;
            </a>
        </p>
        '''

    return f'''
    <div class="empty-description-card">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        <h3>Full Role Details Available on Employer Site</h3>
        <p>A full text description was not included in this listing feed. Please visit the company's official posting to view all responsibilities, team requirements, and submit your application.</p>
        {button_html}
    </div>
    '''
