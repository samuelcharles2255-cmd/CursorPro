from django.test import Client, TestCase
from apps.jobs.models import Company, Job
from apps.jobs.cleaning import clean_job_description


class JobDescriptionCleaningTests(TestCase):
    def test_strip_html_artifacts_and_classes(self):
        raw_html = '''<div class="JobPostPage-content ⚙ ⚙1opjj73">
        <h3 id="about-stripe">About Stripe</h3>
        <p>Stripe is a financial infrastructure platform for businesses.</p>
        <ul>
        <li>* 8+ years of sales experience</li>
        </ul>
        </div>'''
        cleaned = clean_job_description(raw_html)
        self.assertNotIn("⚙", cleaned)
        self.assertNotIn("JobPostPage-content", cleaned)
        self.assertNotIn("<div", cleaned)
        self.assertIn("<h3>About Stripe</h3>", cleaned)
        self.assertIn("<li>8+ years of sales experience</li>", cleaned)

    def test_encoded_html_unescaped_and_sanitized(self):
        raw_encoded = "&lt;h2&gt;Who we are&lt;/h2&gt;&lt;p&gt;Overview text&lt;/p&gt;"
        cleaned = clean_job_description(raw_encoded)
        self.assertIn("<h2>Who we are</h2>", cleaned)
        self.assertIn("<p>Overview text</p>", cleaned)

    def test_search_snippet_cleaning(self):
        raw_snippet = (
            "&nbsp;...dashboard for real-time monitoring, alerting across layers. \n"
            " Skills & Tools:  Utilize Ansible, <b>Python,</b> PowerShell to deliver solutions. \n\n"
            " Job Skill Requirements...&nbsp;..........................&nbsp;...Work independently. \n\n"
            "     SKILLS & EXPERIENCE REQUIRED  \n"
            "  Strong <b>Python </b>skills (Python 3.11+ preferred).  \n"
            "  Hands-on experience with Django/FastAPI and...&nbsp;"
        )
        cleaned = clean_job_description(raw_snippet, source="api")
        self.assertNotIn("&nbsp;", cleaned)
        self.assertNotIn("<b>", cleaned)
        self.assertNotIn("</b>", cleaned)
        self.assertNotIn("................", cleaned)
        self.assertIn("Python,", cleaned)
        self.assertIn("<h3>SKILLS &amp; EXPERIENCE REQUIRED</h3>", cleaned)

    def test_xss_sanitization(self):
        xss_input = '<p>Normal text</p><script>alert("XSS")</script><a href="javascript:alert(1)">Click</a>'
        cleaned = clean_job_description(xss_input)
        self.assertNotIn("<script>", cleaned)
        self.assertNotIn("javascript:", cleaned)
        self.assertIn("<p>Normal text</p>", cleaned)


class JobDetailViewRenderingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name="Acme Corp",
            website="https://acme.example.com",
            country="United States",
        )

    def test_job_detail_renders_clean_html_without_escaping_tags(self):
        job = Job.objects.create(
            title="Senior Engineer",
            company=self.company,
            source="career_page",
            source_job_id="acme_1",
            description="<p>Welcome to Acme Corp.</p><ul><li>Build great products</li></ul>",
            application_url="https://acme.example.com/jobs/1",
        )
        response = self.client.get(f"/jobs/{job.id}/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("<p>Welcome to Acme Corp.</p>", content)
        self.assertIn("<li>Build great products</li>", content)
        self.assertNotIn("&lt;p&gt;Welcome", content)

    def test_empty_description_renders_placeholder_card(self):
        job = Job.objects.create(
            title="SRE",
            company=self.company,
            source="career_page",
            source_job_id="acme_2",
            description="",
            application_url="https://acme.example.com/jobs/2",
        )
        response = self.client.get(f"/jobs/{job.id}/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("empty-description-card", content)
        self.assertIn("Full Role Details Available on Employer Site", content)
