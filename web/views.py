from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST

from accounts.models import EmployerProfile, Profile
from apps.jobs.models import Company, Job, Skill

from .forms import (
    AccountForm,
    ChangePasswordForm,
    EmployerProfileForm,
    JobFilterForm,
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    ProfileForm,
    RegisterForm,
)

User = get_user_model()
PAGE_SIZE = 12


def _active_jobs():
    return Job.objects.select_related("company").prefetch_related("skills")


def _exclude_expired(qs):
    return qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now()))


def home(request):
    jobs = _exclude_expired(_active_jobs())
    featured = jobs[:6]
    matching = []
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        skill_ids = list(profile.skills.values_list("id", flat=True))
        if skill_ids:
            matching = (
                _exclude_expired(_active_jobs())
                .filter(skills__in=skill_ids)
                .distinct()[:6]
            )
    context = {
        "featured_jobs": featured,
        "matching_jobs": matching,
        "job_count": jobs.count(),
        "company_count": Company.objects.filter(active=True).count(),
        "skill_count": Skill.objects.count(),
        "countries": (
            jobs.exclude(country="")
            .values_list("country", flat=True)
            .distinct()
            .order_by("country")[:8]
        ),
    }
    return render(request, "pages/home.html", context)


def job_list(request):
    qs = _active_jobs()
    include_expired = request.GET.get("include_expired") in ("true", "on", "1")
    if not include_expired:
        qs = _exclude_expired(qs)

    countries = (
        Job.objects.exclude(country="")
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )
    companies = Company.objects.filter(active=True)
    form = JobFilterForm(request.GET or None, countries=countries, companies=companies)

    if form.is_valid():
        data = form.cleaned_data
        search = (data.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
                | Q(company__name__icontains=search)
                | Q(skills__name__icontains=search)
            ).distinct()
        if data.get("employment_type"):
            qs = qs.filter(employment_type=data["employment_type"])
        if data.get("country"):
            qs = qs.filter(country=data["country"])
        if data.get("company"):
            qs = qs.filter(company=data["company"])
        ordering = data.get("ordering") or "-posted_at"
        allowed = {"-posted_at", "posted_at", "-salary_max", "salary_min"}
        qs = qs.order_by(ordering if ordering in allowed else "-posted_at")

    paginator = Paginator(qs, PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "jobs/list.html",
        {
            "form": form,
            "page": page,
            "jobs": page.object_list,
            "include_expired": include_expired,
        },
    )


def job_detail(request, pk):
    job = get_object_or_404(_active_jobs(), pk=pk)
    related = (
        _exclude_expired(_active_jobs())
        .filter(Q(company=job.company) | Q(skills__in=job.skills.all()))
        .exclude(pk=job.pk)
        .distinct()[:4]
    )
    overlap = []
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        user_skills = set(profile.skills.values_list("id", flat=True))
        overlap = [s for s in job.skills.all() if s.id in user_skills]
    return render(
        request,
        "jobs/detail.html",
        {"job": job, "related_jobs": related, "matching_skills": overlap},
    )


def company_list(request):
    qs = Company.objects.annotate(job_count=Count("jobs")).order_by("name")
    search = (request.GET.get("search") or "").strip()
    if search:
        qs = qs.filter(name__icontains=search)
    paginator = Paginator(qs, 18)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "companies/list.html",
        {"page": page, "companies": page.object_list, "search": search},
    )


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    jobs = _exclude_expired(_active_jobs().filter(company=company))
    return render(request, "companies/detail.html", {"company": company, "jobs": jobs})


def register(request):
    if request.user.is_authenticated:
        return redirect("web:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome. Your account is ready.")
        if user.is_employer:
            return redirect("web:employer_profile")
        return redirect("web:profile")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("web:home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.user)
        messages.success(request, f"Signed in as {form.user.email}.")
        next_url = request.GET.get("next") or reverse("web:home")
        return redirect(next_url)
    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("web:home")


@login_required
def account(request):
    form = AccountForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account updated.")
        return redirect("web:account")
    return render(request, "accounts/account.html", {"form": form})


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile_obj)
    matching = []
    skill_ids = list(profile_obj.skills.values_list("id", flat=True))
    if skill_ids:
        matching = (
            _exclude_expired(_active_jobs())
            .filter(skills__in=skill_ids)
            .distinct()[:6]
        )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile saved. Matching jobs will use these skills.")
        return redirect("web:profile")
    return render(
        request,
        "accounts/profile.html",
        {"form": form, "profile": profile_obj, "matching_jobs": matching},
    )


@login_required
def employer_profile(request):
    if not request.user.is_employer:
        messages.error(request, "This account is not an employer account.")
        return redirect("web:profile")
    profile_obj, _ = EmployerProfile.objects.get_or_create(user=request.user)
    form = EmployerProfileForm(request.POST or None, instance=profile_obj)
    company_jobs = []
    if profile_obj.company_id:
        company_jobs = _exclude_expired(_active_jobs().filter(company=profile_obj.company))[:8]
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employer profile saved.")
        return redirect("web:employer_profile")
    return render(
        request,
        "accounts/employer_profile.html",
        {"form": form, "employer": profile_obj, "company_jobs": company_jobs},
    )


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.user.set_password(form.cleaned_data["new_password"])
        request.user.save()
        login(request, request.user)
        messages.success(request, "Password updated.")
        return redirect("web:account")
    return render(request, "accounts/change_password.html", {"form": form})


def password_reset_request(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_path = request.build_absolute_uri(
                reverse("web:password_reset_confirm", args=[uid, token])
            )
            send_mail(
                subject="Reset your password",
                message=f"Use this link to reset your password: {reset_path}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[user.email],
            )
        messages.info(request, "If that email exists, a reset link has been sent.")
        return redirect("web:login")
    return render(request, "accounts/password_reset.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "This reset link is invalid or has expired.")
        return redirect("web:password_reset")

    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password"])
        user.save()
        messages.success(request, "Password reset. Log in with your new password.")
        return redirect("web:login")
    return render(request, "accounts/password_reset_confirm.html", {"form": form})
