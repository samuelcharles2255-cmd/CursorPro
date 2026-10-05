import json
from datetime import date, timedelta
from bs4 import BeautifulSoup
from apps.jobs.services.base import (
    NormalizedJob, BaseScraper,
    parse_date, normalize_location,
    extract_jobposting_jsonld, jobposting_to_normalized,
)
from apps.jobs.services.nmb import NMBScraper
from apps.jobs.services.equity import EquityScraper
from apps.jobs.services.browser import BrowserJsonScraper, looks_like_jobs, pick, TITLE
from apps.jobs.services.boards import JsonLdBoardScraper

failures = 0


def check(name, cond, extra=""):
    global failures
    print(("PASS " if cond else "FAIL ") + name, extra if not cond else "")
    if not cond:
        failures += 1


def run_checks():
    # ---------- normalizers
    check("date dd-Mon-yyyy", parse_date("30-Sep-2026") == date(2026,9,30))
    check("date 'Oct 02 2026'", parse_date("Oct 02 2026") == date(2026,10,2))
    check("date ordinal+weekday", parse_date("Friday 2nd October 2026") == date(2026,10,2))
    check("date iso datetime", parse_date("2026-08-13T00:00:00Z") == date(2026,8,13))
    check("date dd/mm/yyyy day-first", parse_date("13/08/2026") == date(2026,8,13))
    check("date epoch ms", parse_date(1790000000000) is not None)
    check("date junk", parse_date("soon") is None)
check("loc Dar es-Salaam", normalize_location("Dar Es-Salaam") == "Dar es Salaam, Tanzania", normalize_location("Dar Es-Salaam"))
check("loc empty", normalize_location("") == "Tanzania")
check("loc Head Office", normalize_location("Head Office, Hq") == "Head Office, Hq, Tanzania", normalize_location("Head Office, Hq"))
check("loc TZ", normalize_location("Mbeya, TZ") == "Mbeya, Tanzania", normalize_location("Mbeya, TZ"))

# ---------- NMB fixture (structure mirrors the live page text)
def vac(i, title, loc, purpose, o, c):
    loc_html = f"<b>Job Location :</b> {loc}<br>" if loc else ""
    return f"""<tr><td><span>{title} (1 Position(s))</span><br>{loc_html}
    <b>Job Purpose:</b> {purpose}<br><b>Main Responsibilities:</b><br><ul><li>Do A</li><li>Do B</li></ul>
    <b>Qualifications and Experience:</b> Degree.<br>*NMB Bank Plc is an Equal Opportunity Employer*<br>
    Job opening date : {o} <br> Job closing date : {c}
    <a href="javascript:__doPostBack('dlVaanciesList$ctl0{i}$btnApply','')">Login to Apply</a></td></tr>"""
nmb_html = "<html><body><h4>Vacancies (3)</h4><table id='dlVaanciesList'>" + \
    vac(0,"NOC Infrastructure Specialist","Head Office, Hq","Monitor incidents.","16-Sep-2026","30-Sep-2026") + \
    vac(1,"Relationship Manager; Special Lending",None,"Drive lending growth.","16-Sep-2026","30-Sep-2026") + \
    vac(2,"Relationship Manager; Commercial - Chinese Desk","Highlands Zone","Advise on Chinese business.","14-Sep-2026","28-Sep-2026") + \
    "</table><span>Position(s)</span></body></html>"
s = NMBScraper()
jobs = [j.finalize() for j in s.parse_text(BeautifulSoup(nmb_html, "html.parser").get_text("\n"))]
check("nmb count == 3", len(jobs) == 3, len(jobs))
check("nmb title clean", jobs[0].title == "NOC Infrastructure Specialist", jobs[0].title)
check("nmb no header junk in title 1", "Vacancies" not in jobs[0].title)
check("nmb location", jobs[0].location == "Head Office, Hq, Tanzania", jobs[0].location)
check("nmb missing location -> Tanzania", jobs[1].location == "Tanzania", jobs[1].location)
check("nmb deadline", jobs[0].deadline == date(2026,9,30))
check("nmb desc has purpose+bullets", "Monitor incidents." in jobs[0].description and "Do A" in jobs[0].description, jobs[0].description)
check("nmb desc excludes dates", "opening date" not in jobs[0].description)
check("nmb org", jobs[0].organization == "NMB Bank Plc")
check("nmb apply url", jobs[0].apply_url.startswith("https://careers.nmbbank"))
check("nmb ext ids unique", len({j.external_id for j in jobs}) == 3)
check("nmb title w/ semicolon+dash", jobs[2].title == "Relationship Manager; Commercial - Chinese Desk", jobs[2].title)

# ---------- Equity fixture
eq_html = """<html><body><div class='x'>Head Office</div>
<div class='job'><span class='d'>Aug 05 2028</span><h5>Senior Officer – Card Operations</h5><p>Manage card operations.</p><a href='/tz/uploads/JD-Card.pdf'>View Details</a></div>
<div class='job'><span class='d'>Oct 02 2026</span><h5>Valuation Officer</h5><p>Review valuations.</p><a href='/tz/uploads/JD---Valuation-Officer.pdf'>View Details</a></div>
<div class='job'><h5>Undated Role</h5><p>No date shown.</p><a href='/tz/uploads/JD-U.pdf'>View Details</a></div>
<h5>Footer heading</h5></body></html>"""
ej = [j.finalize() for j in EquityScraper().parse(BeautifulSoup(eq_html, "html.parser"))]
check("equity count == 3 (footer h5 skipped)", len(ej) == 3, [j.title for j in ej])
check("equity 2028 typo dropped", ej[0].deadline is None and ej[0].warnings, ej[0].deadline)
check("equity deadline parsed", ej[1].deadline == date(2026,10,2), ej[1].deadline)
check("equity no date bleed from previous job", ej[2].deadline is None, ej[2].deadline)
check("equity pdf in description", "JD---Valuation-Officer.pdf" in ej[1].description)
check("equity mailto", ej[1].apply_url.startswith("mailto:TZRecruitment@equitybank.co.tz?subject=Valuation"))
check("equity location", ej[1].location == "Head Office, Tanzania", ej[1].location)

# ---------- JSON-LD board parsing
ld = {"@context":"https://schema.org","@type":"JobPosting","title":"Data Analyst","description":"<p>Analyse <b>data</b>.</p><ul><li>SQL</li></ul>",
      "validThrough":"2026-10-15T23:59:00+03:00","hiringOrganization":{"@type":"Organization","name":"Acme TZ"},
      "jobLocation":{"@type":"Place","address":{"@type":"PostalAddress","addressLocality":"Dar es Salaam","addressCountry":"TZ"}},"url":"https://x.test/job/1"}
page = BeautifulSoup(f'<script type="application/ld+json">{json.dumps({"@graph":[{"@type":"WebSite"}, ld]})}</script>', "html.parser")
node = extract_jobposting_jsonld(page)
check("jsonld found in @graph", node is not None)
nj = jobposting_to_normalized(node, "fuzu", "https://x.test/job/1").finalize()
check("jsonld fields", (nj.title, nj.organization, nj.deadline, nj.location) == ("Data Analyst","Acme TZ",date(2026,10,15),"Dar es Salaam, Tanzania"), (nj.title,nj.organization,nj.deadline,nj.location))
check("jsonld description html->text", "Analyse data." in nj.description and "SQL" in nj.description, nj.description)

class B(JsonLdBoardScraper):
    key="b"; LINK_PATTERN=r"^/listings?/"
links = B().detail_links(BeautifulSoup('<a href="/listings/a-1">a</a><a href="/listings/a-1#x">dup</a><a href="/about">n</a><a href="https://other.com/listings/z">ext</a>', "html.parser"), "https://bm.test/jobs")
check("board link filter", links == ["https://bm.test/listings/a-1"], links)

# ---------- browser JSON sniffing (fake API payloads)
payload_ajira = {"data": {"content": [
  {"id": 101, "jobTitle": "Procurement Officer II", "employerName": "Bank of Tanzania", "dutyStation": "Dodoma", "closingDate": "2026-10-09", "description": "<p>Do procurement</p>"},
  {"id": 102, "jobTitle": "Driver II", "employerName": "TPA", "dutyStation": "Mbeya", "closingDate": 1791000000000}]},
  "menu": [{"name": "Home"}, {"name": "About"}]}
noise = {"regions": [{"name": "Arusha"}, {"name": "Dodoma"}]}
class T(BrowserJsonScraper):
    key="t"; START_URL="https://portal.example/vacancies"; DEFAULT_ORG="PSRS"; DETAIL_URL_TEMPLATE="https://portal.example/vacancies/{id}"
    def _render(self): return [("https://api.example/v1/adverts?page=1", payload_ajira), ("https://api.example/regions", noise)]
tj = T().scrape()
check("sniff picks jobs, ignores menu/regions", [j.title for j in tj] == ["Procurement Officer II","Driver II"], [j.title for j in tj])
check("sniff maps org/loc/deadline", (tj[0].organization, tj[0].location, tj[0].deadline) == ("Bank of Tanzania","Dodoma, Tanzania",date(2026,10,9)), (tj[0].organization, tj[0].location, tj[0].deadline))
check("sniff epoch deadline", tj[1].deadline is not None, tj[1].deadline)
check("sniff detail url", tj[0].apply_url == "https://portal.example/vacancies/101", tj[0].apply_url)
class E(T):
    def _render(self): return [("https://x/y", noise)]
try:
    E().scrape(); check("sniff raises loud when nothing found", False)
except RuntimeError as e:
    check("sniff raises loud when nothing found", "no job-like JSON" in str(e))
class V(T):
    LOCATION_MUST_MATCH = r"tanzania|dar es"
    def _render(self): return [("https://x/jobs", {"jobs":[{"id":1,"title":"Fraud Analyst","location":"Dar es-Salaam, Tanzania","closingDate":"2026-10-30"},{"id":2,"title":"Energy Engineer","location":"Midrand, South Africa","closingDate":"2026-10-30"}]})]
vj = V().scrape()
check("vodacom-style tz filter", [j.title for j in vj] == ["Fraud Analyst"], [j.title for j in vj])

# ---------- scrape(): expired + dup handling
class X(BaseScraper):
    key="x"
    def fetch(self):
        yield NormalizedJob("x","Old","Org","", date.today()-timedelta(days=3),"","https://a")
        yield NormalizedJob("x","New","Org","", date.today()+timedelta(days=3),"","https://a")
        yield NormalizedJob("x","New","Org","", date.today()+timedelta(days=3),"","https://a")
        yield NormalizedJob("x","","Org","", None,"","https://a")
xs = X(); xj = xs.scrape()
check("expired dropped, dup dropped, invalid dropped", [j.title for j in xj]==["New"] and xs.stats["expired"]==1 and xs.stats["duplicates"]==1 and xs.stats["skipped_invalid"]==1, xs.stats)
print("\nFAILURES:", failures)
