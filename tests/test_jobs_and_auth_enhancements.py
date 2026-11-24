import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.jobs.models import Company, Job, Skill, JobApplication, SavedJob
from apps.marketplace.categories.models import Category
from apps.marketplace.listings.models import Listing
from apps.marketplace.favorites.models import Favorite
from users.models import PhoneVerificationOTP, UserProfile

UserModel = get_user_model()


class JobsAndAuthEnhancementAPITests(APITestCase):
    def setUp(self):
        self.candidate = UserModel.objects.create_user(
            username="candidate_jane",
            email="candidate@atrium.test",
            phone_number="+255755111222",
            password="StrongPassword123!",
            role="buyer"
        )
        UserProfile.objects.get_or_create(user=self.candidate, defaults={"region": "Dar es Salaam"})

        self.seller = UserModel.objects.create_user(
            username="merchant_john",
            email="merchant@atrium.test",
            phone_number="+255755333444",
            password="StrongPassword123!",
            role="seller"
        )

        self.company = Company.objects.create(
            name="Apex Horizon Capital",
            country="Tanzania",
            website="https://apexhorizon.co.tz"
        )

        self.job = Job.objects.create(
            title="Principal Cloud Systems Architect",
            company=self.company,
            location="Dar es Salaam, Tanzania",
            country="Tanzania",
            description="Lead cloud infrastructure migration across EAC banking hubs.",
            employment_type="full_time",
            salary_min=Decimal("12000000.00"),
            salary_max=Decimal("18000000.00"),
            salary_currency="TSh",
            application_url="https://apexhorizon.co.tz/careers/cloud-arch",
            posted_at=timezone.now()
        )

        self.category = Category.objects.create(name="Fine Tech", icon="cpu")
        self.listing = Listing.objects.create(
            seller=self.seller,
            category=self.category,
            title="Hasselblad X2D 100C Medium Format Camera",
            description="100MP medium format CMOS sensor, complete kit with 55mm f/2.5 lens.",
            price=Decimal("24500000.00"),
            status=Listing.STATUS_ACTIVE
        )

    # =========================================================================
    # 1. JOB APPLICATIONS WORKFLOW
    # =========================================================================
    def test_job_application_submission_and_retrieval(self):
        self.client.force_authenticate(user=self.candidate)

        payload = {
            "job": self.job.id,
            "full_name": "Jane Mwangi",
            "email": "candidate@atrium.test",
            "phone": "+255755111222",
            "cover_letter": "10+ years engineering high-availability banking infrastructures.",
        }

        # Submit Application
        res = self.client.post("/api/job-applications/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["job"], self.job.id)
        self.assertEqual(res.data["status"], "SUBMITTED")
        self.assertEqual(res.data["company_name"], self.company.name)

        # Duplicate application rejected
        dup_res = self.client.post("/api/job-applications/", payload, format="json")
        self.assertEqual(dup_res.status_code, status.HTTP_400_BAD_REQUEST)

        # List candidate applications
        list_res = self.client.get("/api/job-applications/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        results = list_res.data if isinstance(list_res.data, list) else list_res.data.get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["job_title"], self.job.title)

    # =========================================================================
    # 2. SAVED JOBS WORKFLOW
    # =========================================================================
    def test_saved_job_toggle_and_list(self):
        self.client.force_authenticate(user=self.candidate)

        # Save job
        res_save = self.client.post("/api/saved-jobs/toggle/", {"job_id": self.job.id})
        self.assertEqual(res_save.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res_save.data["saved"])

        # Check list
        res_list = self.client.get("/api/saved-jobs/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        results = res_list.data if isinstance(res_list.data, list) else res_list.data.get("results", [])
        self.assertEqual(len(results), 1)

        # Unsave job
        res_unsave = self.client.post("/api/saved-jobs/toggle/", {"job_id": self.job.id})
        self.assertEqual(res_unsave.status_code, status.HTTP_200_OK)
        self.assertFalse(res_unsave.data["saved"])

    # =========================================================================
    # 3. PASSWORD CHANGE & RESET
    # =========================================================================
    def test_password_change(self):
        self.client.force_authenticate(user=self.candidate)

        # Fail with wrong old password
        res_fail = self.client.post("/api/auth/password/change/", {
            "old_password": "WrongPassword999!",
            "new_password": "NewStrongPassword777!"
        })
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # Succeed with correct old password
        res_ok = self.client.post("/api/auth/password/change/", {
            "old_password": "StrongPassword123!",
            "new_password": "NewStrongPassword777!"
        })
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)

        # Verify new password allows login
        self.client.logout()
        login_res = self.client.post("/api/auth/login/", {
            "email": "candidate@atrium.test",
            "password": "NewStrongPassword777!"
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    def test_password_reset_flow(self):
        # 1. Request reset
        req_res = self.client.post("/api/auth/password/reset/", {
            "email": "merchant@atrium.test"
        })
        self.assertEqual(req_res.status_code, status.HTTP_200_OK)

        # Fetch generated OTP from DB
        otp_record = PhoneVerificationOTP.objects.filter(
            phone_number=self.seller.phone_number,
            is_used=False
        ).order_by("-created_at").first()
        self.assertIsNotNone(otp_record)

        # 2. Confirm reset
        confirm_res = self.client.post("/api/auth/password/reset/confirm/", {
            "email": "merchant@atrium.test",
            "code": otp_record.otp_code,
            "new_password": "BrandNewPassword888!"
        })
        self.assertEqual(confirm_res.status_code, status.HTTP_200_OK)

        # 3. Login with newly reset password
        login_res = self.client.post("/api/auth/login/", {
            "email": "merchant@atrium.test",
            "password": "BrandNewPassword888!"
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
