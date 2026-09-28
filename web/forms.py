from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation

from accounts.models import EmployerProfile, Profile
from apps.jobs.models import Company, Skill

User = get_user_model()


def _styled(field, extra=""):
    css = f"field-input {extra}".strip()
    existing = field.widget.attrs.get("class", "")
    field.widget.attrs["class"] = f"{existing} {css}".strip()
    return field


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault("class", "skill-options")
            elif isinstance(field.widget, forms.Textarea):
                _styled(field, "field-textarea")
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                _styled(field, "field-select")
            else:
                _styled(field)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["email", "name", "role", "password", "password2"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "field-input", "autocomplete": "email"}),
            "name": forms.TextInput(attrs={"class": "field-input", "autocomplete": "name"}),
            "role": forms.Select(attrs={"class": "field-input field-select"}),
        }

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("password2"):
            self.add_error("password2", "Passwords don't match.")
        if data.get("password"):
            password_validation.validate_password(data["password"])
        return data

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            name=self.cleaned_data.get("name") or "",
            role=self.cleaned_data["role"],
        )
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
            if user.role == User.ROLE_EMPLOYER:
                EmployerProfile.objects.get_or_create(user=user)
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "field-input", "autocomplete": "email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "current-password"})
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive.")
            self.user = user
        return data


class ProfileForm(StyledModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "location", "phone", "resume_url", "avatar_url", "skills"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5, "placeholder": "A short professional summary"}),
            "location": forms.TextInput(attrs={"placeholder": "City, country"}),
            "phone": forms.TextInput(attrs={"placeholder": "+255 …"}),
            "resume_url": forms.URLInput(attrs={"placeholder": "https://…"}),
            "avatar_url": forms.URLInput(attrs={"placeholder": "https://…"}),
            "skills": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skills"].queryset = Skill.objects.all()
        self.fields["skills"].required = False
        self.fields["resume_url"].required = False
        self.fields["avatar_url"].required = False


class EmployerProfileForm(StyledModelForm):
    class Meta:
        model = EmployerProfile
        fields = ["company", "job_title"]
        widgets = {
            "job_title": forms.TextInput(attrs={"placeholder": "e.g. HR Manager"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(active=True)
        self.fields["company"].required = False


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field-input", "autocomplete": "name"}),
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "current-password"})
    )
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        password = self.cleaned_data["old_password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("Wrong password.")
        return password

    def clean(self):
        data = super().clean()
        if data.get("new_password") != data.get("new_password2"):
            self.add_error("new_password2", "Passwords don't match.")
        if data.get("new_password"):
            password_validation.validate_password(data["new_password"], self.user)
        return data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "field-input", "autocomplete": "email"})
    )


class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
    )

    def clean(self):
        data = super().clean()
        if data.get("new_password") != data.get("new_password2"):
            self.add_error("new_password2", "Passwords don't match.")
        if data.get("new_password"):
            password_validation.validate_password(data["new_password"])
        return data


class JobFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "field-input",
                "placeholder": "Title, skill, or city",
                "name": "search",
            }
        ),
    )
    employment_type = forms.ChoiceField(
        required=False,
        choices=[("", "All types")],
        widget=forms.Select(attrs={"class": "field-input field-select"}),
    )
    country = forms.ChoiceField(
        required=False,
        choices=[("", "All countries")],
        widget=forms.Select(attrs={"class": "field-input field-select"}),
    )
    company = forms.ModelChoiceField(
        required=False,
        queryset=Company.objects.none(),
        empty_label="All companies",
        widget=forms.Select(attrs={"class": "field-input field-select"}),
    )
    ordering = forms.ChoiceField(
        required=False,
        choices=[
            ("-posted_at", "Newest first"),
            ("posted_at", "Oldest first"),
            ("-salary_max", "Highest salary"),
            ("salary_min", "Lowest salary"),
        ],
        widget=forms.Select(attrs={"class": "field-input field-select"}),
    )
    include_expired = forms.BooleanField(required=False, label="Include expired listings")

    def __init__(self, *args, countries=None, companies=None, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.jobs.models import Job

        self.fields["employment_type"].choices = [("", "All types")] + list(Job.EMPLOYMENT_CHOICES)
        country_choices = [("", "All countries")]
        for country in countries or []:
            if country:
                country_choices.append((country, country))
        self.fields["country"].choices = country_choices
        self.fields["company"].queryset = companies if companies is not None else Company.objects.all()
