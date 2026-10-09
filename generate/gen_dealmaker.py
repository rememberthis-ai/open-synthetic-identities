#!/usr/bin/env python3
"""Generate the deal-maker fixture: an invented corporate-finance boutique, two ways of keeping its deals.

Everything here is invented: the firm, the people, the companies, the investors, the domains (`.example`)
and the iMessage handles (email addresses, so no phone number can be anyone's). Nothing is from anyone's
real contacts or pipeline. It is shaped like the people The Revenue Assistant (https://therevenueassistant.com)
is for: a small advisory that works companies AND investors.

    python3 generate/gen_dealmaker.py

writes, into fixtures/revenueassistant/dealmaker/:
- `shared/`  mail (.eml), calendar.ics, iMessage threads, the newsletter's activity export, a site summary:
             the same in both variants;
- `crm/`     variant A: a Pipedrive-style CSV export (organizations, persons, deals, activities);
- `folder/`  variant B: a shared folder used as the CRM: `Prospects.xlsx` (+ the same sheets as CSV) and a
             OneNote-style export, one page per meeting and one log page per company;
- `truth.json` and `ANSWER-KEY.md`: each party's ring and sector, and why, from what the sources show.

The firm is Lindgate Advisory (two partners, Johan Aalto and Sofia Berglund). "Today" is TODAY below.
Mail, calendar and iMessage cover the last four months only; anything older lives only in the CRM or the
folder, so the scan has to read those to place the long relationships.

The truth uses only the event words of the apps' map record format; a dated step with no word is recorded as
nothing, and ANSWER-KEY.md lists it.
"""
import csv
import datetime as dt
import json
import os
import shutil

TODAY = dt.date(2026, 10, 9)
WINDOW_START = dt.date(2026, 6, 1)  # mail, calendar and iMessage exports start here
HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures", "revenueassistant", "dealmaker")
FIRM = "Lindgate Advisory"
MAP = "lindgate"
TEAM = {
    "johan": ("Johan Aalto", "johan@lindgate.example"),
    "sofia": ("Sofia Berglund", "sofia@lindgate.example"),
}

# --- the cast -----------------------------------------------------------------------------------------
# slug: name, type, kind (who they are TO Lindgate), sector (who pulled them in), owner, contact (name,
# email, role) for organisations, city, and the answer key's reason.

P = {}


def party(slug, name, type_, kind, sector, owner, why, contact=None, city="", org=None, not_now=None, no=None):
    # no: "map" (a no to Lindgate: not_now on the party) or "deal" (a no to one deal: the deal is lost)
    P[slug] = dict(slug=slug, name=name, type=type_, kind=kind, sector=sector, owner=owner, why=why,
                   contact=contact, city=city, org=org, not_now=not_now, no=no or ("map" if not_now else None))


# Clients and prospects (kind customer): companies that hire Lindgate for a sale, an acquisition or a raise.
party("vaara-packaging", "Vaara Packaging Oy", "organisation", "customer", "team", "johan",
      "Johan's own relationship from 2025; sale closed 2026-06-30 (outcome). Older history is only in the CRM/folder.",
      ("Antti Vaara", "antti@vaara-packaging.example", "CEO and owner"), "Lahti, FI")
party("harju-logistics", "Harju Logistics Oy", "organisation", "customer", "team", "johan",
      "Sale closed in March (outcome), hired again for an add-on acquisition in August (reordered), then Petra "
      "introduced Tammela Steel (referred).",
      ("Petra Harju", "petra@harju-logistics.example", "CEO"), "Tampere, FI")
party("tammela-steel", "Tammela Steel Oy", "organisation", "customer", "referrals", "johan",
      "Came through Petra Harju's introduction (referrals, via harju-logistics); asked to meet, and met.",
      ("Jari Tammela", "jari@tammela-steel.example", "CEO"), "Hämeenlinna, FI")
party("kallio-foods", "Kallio Foods Oy", "organisation", "customer", "team", "johan",
      "Johan's relationship; engagement letter signed in June and Project Birch kicked off (set_up). The deal "
      "has not closed, so no outcome yet.",
      ("Mari Kallio", "mari@kallio-foods.example", "CEO"), "Turku, FI")
party("vesi-analytics", "Vesi Analytics Oy", "organisation", "customer", "team", "johan",
      "Met and asked for a proposal in the spring, then said not now (revisit after the 2026 accounts). "
      "Everything is older than the mail export: only the CRM/folder shows it. Needs not_now.",
      ("Oskari Vesi", "oskari@vesi-analytics.example", "Founder"), "Espoo, FI", not_now="2027-03-01")
party("nordvent-systems", "Nordvent Systems AB", "organisation", "customer", "referrals", "johan",
      "Elina Saari introduced Camilla Nord by email (a person's introduction, no fee: referrals, via elina-saari). "
      "Asked how a sale process would run. The CRM stage says 'Proposal made'; no proposal is in any source.",
      ("Camilla Nord", "camilla@nordvent.example", "CEO"), "Uppsala, SE")
party("okko-instruments", "Okko Instruments Oy", "organisation", "customer", "partner_sales", "sofia",
      "Passed on by Merikoski Bank under its referral agreement (a company bringing clients as its business: "
      "partner_sales, via merikoski-bank). Asked for a proposal.",
      ("Sanna Okko", "sanna@okko-instruments.example", "Managing director"), "Oulu, FI")
party("lumo-health", "Lumo Health Oy", "organisation", "customer", "organic", "sofia",
      "Wrote after reading Lindgate's article on selling a founder-owned company (found us: organic) and asked "
      "for a call.",
      ("Ville Kuosmanen", "ville@lumo-health.example", "Co-founder"), "Helsinki, FI")
party("brannvik-marine", "Brannvik Marine AB", "organisation", "customer", "audience", "johan",
      "Subscribed to the quarterly letter, then replied to the Q3 issue asking about valuations (asked_info, audience).",
      ("Erik Brannvik", "erik@brannvik-marine.example", "Owner"), "Göteborg, SE")
party("kuusi-robotics", "Kuusi Robotics Oy", "organisation", "customer", "audience", "sofia",
      "Subscribed to the quarterly letter and opened the Q3 issue; nothing more (audience).",
      ("Helmi Kuusi", "helmi@kuusi-robotics.example", "CEO"), "Jyväskylä, FI")
party("oravala-software", "Oravala Software Oy", "organisation", "customer", "paid", "johan",
      "Met at the table Lindgate paid to sponsor at the Nordic Mid-Market Forum (bought reach: paid).",
      ("Petteri Oravala", "petteri@oravala.example", "CEO"), "Helsinki, FI")
party("pohjoisranta-dental", "Pohjoisranta Dental Group", "organisation", "customer", "team", "johan",
      "Only a row on Johan's prospect list, no dated interaction anywhere: identified, ring 0. The CRM stage "
      "'Contact made' is the seller's label, not an event.",
      ("Laura Pohjoisranta", "laura@pohjoisranta-dental.example", "CEO"), "Vaasa, FI")
# Investors (kind investor): the funds and people Lindgate places deals with. Treated as deals of their own.
party("revontuli-growth", "Revontuli Growth Partners", "organisation", "investor", "team", "sofia",
      "Sofia's relationship. Asked for the Project Birch teaser, signed the NDA (signed_nda) and sent a "
      "non-binding indicative offer (bid): ring 4.",
      ("Henrik Lund", "henrik@revontuli-growth.example", "Partner"), "Stockholm, SE")
party("kivi-family-office", "Kivi Family Office", "organisation", "investor", "team", "johan",
      "Invested alongside the buyer in the Harju transaction in March (signed, only in the CRM/folder); asked by "
      "text for the Birch teaser in September.",
      ("Leena Kivi", "leena@kivi-family.example", "Investment director"), "Helsinki, FI")
party("fjell-capital", "Fjell Capital AS", "organisation", "investor", "team", "sofia",
      "Passed on Project Birch ('not our sector') but asked to stay on the list for industrials. A no to one deal: "
      "recorded on the Birch deal (status lost, or a declined line there), NOT as a map-wide not_now, which would "
      "silence Fjell for the industrials they asked to hear about.",
      ("Magnus Fjeld", "magnus@fjell-capital.example", "Principal"), "Oslo, NO", no="deal")
party("mikael-rautio", "Mikael Rautio", "person", "investor", "team", "johan",
      "An angel Johan texts. Asked what minority stakes are coming (asked_info), then 'count me in for 100k', a "
      "soft commitment (committed): ring 4.",
      None, "Helsinki, FI")
party("nordic-pension-mutual", "Nordic Pension Mutual", "organisation", "investor", "team", "sofia",
      "Only a row on the investor list: identified, ring 0.",
      ("Kaisa Lehto", "kaisa@npm-pension.example", "Head of private equity"), "Helsinki, FI")
party("strom-holding", "Ström Holding AB", "organisation", "investor", "team", "johan",
      "Only a row on the investor list: identified, ring 0.",
      ("Anders Ström", "anders@strom-holding.example", "Owner"), "Stockholm, SE")
# Partners (kind partner): people and firms that bring mandates.
party("elina-saari", "Elina Saari", "person", "partner", "team", "johan",
      "A lawyer Johan has known since 2025 (team). Introduced Nordvent's CEO in August (introduced: ring 4).",
      None, "Helsinki, FI", org="Saari & Co")
party("merikoski-bank", "Merikoski Bank", "organisation", "partner", "team", "sofia",
      "Sofia's relationship. A referral agreement was signed in April (signed, only in the CRM/folder), and the "
      "corporate desk introduced Okko Instruments in September (introduced).",
      ("Tuomas Leino", "tuomas@merikoski-bank.example", "Head of corporate banking"), "Helsinki, FI")

PERSON_EMAIL = {"mikael-rautio": "mikael@rautio.example", "elina-saari": "elina@saari-co.example"}


def contact(slug):
    p = P[slug]
    if p["contact"]:
        return p["contact"][0], p["contact"][1]
    return p["name"], PERSON_EMAIL[slug]


# --- what happened ------------------------------------------------------------------------------------
# (date, party, event word or None, source, what). Source:
#   mail / cal / imsg / news : in the shared exports (only from WINDOW_START on);
#   rec                      : only in the deal records (the CRM's activities, or the folder's notes);
# Event words are the format's. `wrote` is ours; None is a fact with no word (written as a `note`).
EV = []


def e(date, slug, event, src, what, via=None, owner=None, opp=None):
    EV.append(dict(date=dt.date.fromisoformat(date), party=slug, event=event, src=src, what=what, via=via,
                   owner=owner or P[slug]["owner"], opp=opp))


# Vaara: the whole mandate, start to closing.
e("2025-08-21", "vaara-packaging", "met", "rec", "First meeting at their Lahti office; Antti is thinking about selling in 2026")
e("2025-10-02", "vaara-packaging", "signed", "rec", "Engagement letter signed for the sale of the company")
e("2025-10-09", "vaara-packaging", "set_up", "rec", "Kick-off with management; data room opened")
e("2026-06-30", "vaara-packaging", "outcome", "mail", "Antti: the transaction closed today, thank you for getting us there")
# Harju: closed, came back, referred.
e("2025-09-04", "harju-logistics", "met", "rec", "First meeting with Petra in Tampere")
e("2025-09-25", "harju-logistics", "signed", "rec", "Engagement letter signed for the sale of a majority stake")
e("2025-10-01", "harju-logistics", "set_up", "rec", "Kick-off; buyer list agreed")
e("2026-03-31", "harju-logistics", "outcome", "rec", "Transaction closed; majority stake sold to a Nordic buyer")
e("2026-08-17", "harju-logistics", "reordered", "mail", "Petra asks Lindgate to run the add-on acquisition too; new engagement letter attached, signed")
e("2026-09-21", "harju-logistics", "referred", "mail", "Petra introduces Jari Tammela of Tammela Steel, who is thinking about succession")
e("2026-09-22", "tammela-steel", "asked", "mail", "Jari replies to Petra's introduction and asks for a meeting", via="harju-logistics")
e("2026-10-01", "tammela-steel", "met", "cal", "Intro meeting with Jari Tammela")
# Kallio: Project Birch, the live sell-side mandate.
e("2026-05-12", "kallio-foods", "met", "rec", "First meeting with Mari Kallio and the CFO in Turku")
e("2026-06-04", "kallio-foods", "asked_proposal", "mail", "Mari asks for an engagement proposal for selling a majority stake")
e("2026-06-10", "kallio-foods", "wrote", "mail", "Johan sends the engagement proposal")
e("2026-06-16", "kallio-foods", "signed", "mail", "Mari returns the signed engagement letter")
e("2026-06-22", "kallio-foods", "set_up", "cal", "Project Birch kick-off with Kallio management")
e("2026-07-01", "kallio-foods", "paid", "mail", "The CFO confirms the first monthly retainer has been paid")
e("2026-08-27", "kallio-foods", "met", "cal", "Project Birch weekly status")
# Vesi: a no, months before the mail export starts.
e("2026-03-10", "vesi-analytics", "met", "rec", "Met Oskari at his office")
e("2026-04-02", "vesi-analytics", "asked_proposal", "rec", "Oskari asked for a proposal for a minority raise")
e("2026-04-30", "vesi-analytics", "declined", "rec", "Oskari: not now; revisit after the 2026 accounts are out (March 2027)")
# Nordvent: introduced by a lawyer.
e("2026-08-20", "elina-saari", "introduced", "mail", "Elina introduces Camilla Nord of Nordvent Systems by email")
e("2026-08-21", "nordvent-systems", "replied", "mail", "Camilla replies to Elina's introduction", via="elina-saari")
e("2026-08-28", "nordvent-systems", "met", "cal", "First meeting with Camilla Nord")
e("2026-09-15", "nordvent-systems", "asked_info", "mail", "Camilla asks how Lindgate would run a sale process and what it would cost")
e("2025-11-18", "elina-saari", "met", "rec", "Lunch with Elina; she advises founder-owned companies on ownership changes")
# Merikoski Bank and Okko: the partner channel.
e("2026-02-10", "merikoski-bank", "met", "rec", "Sofia met Tuomas Leino at the bank's corporate desk")
e("2026-04-01", "merikoski-bank", "signed", "rec", "Referral agreement signed: the bank passes small sell-side mandates for a fee share")
e("2026-09-24", "merikoski-bank", "introduced", "mail", "Tuomas introduces Sanna Okko of Okko Instruments under the referral agreement")
e("2026-09-25", "okko-instruments", "replied", "mail", "Sanna replies to the bank's introduction", via="merikoski-bank")
e("2026-09-28", "okko-instruments", "asked_proposal", "mail", "Sanna asks for a proposal for selling the company")
e("2026-10-06", "okko-instruments", "met", "cal", "First meeting with Sanna Okko")
# Lumo: found the article.
e("2026-09-05", "lumo-health", "asked", "mail", "Ville writes after reading Lindgate's article on selling a founder-owned company and asks for a call")
e("2026-09-19", "lumo-health", "met", "cal", "Call with Ville Kuosmanen")
# The quarterly letter.
e("2026-06-02", "brannvik-marine", "subscribed", "news", "Subscribed to the quarterly letter")
e("2026-09-08", "brannvik-marine", "asked_info", "mail", "Erik replies to the Q3 letter asking what multiples marine services companies fetch")
e("2026-06-11", "kuusi-robotics", "subscribed", "news", "Subscribed to the quarterly letter")
e("2026-09-07", "kuusi-robotics", "opened", "news", "Opened the Q3 letter")
# The sponsored forum table.
e("2026-09-17", "oravala-software", "met", "cal", "Met Petteri at Lindgate's sponsored table, Nordic Mid-Market Forum")
e("2026-09-18", "oravala-software", "replied", "mail", "Petteri replies to the follow-up; wants to talk again in Q1")
# Investors on Project Birch.
e("2026-01-27", "revontuli-growth", "met", "rec", "Sofia met Henrik Lund at Revontuli's Stockholm office")
e("2026-07-08", "revontuli-growth", "asked_info", "mail", "Henrik asks for the Project Birch teaser", opp="birch")
e("2026-07-14", "revontuli-growth", "signed_nda", "mail", "Henrik returns the signed NDA for Project Birch", opp="birch")
e("2026-08-20", "revontuli-growth", "asked", "imsg", "Henrik asks by text for a management meeting with Kallio", opp="birch")
e("2026-09-10", "revontuli-growth", "bid", "mail", "Revontuli's non-binding indicative offer for Project Birch arrives", opp="birch")
e("2025-11-06", "kivi-family-office", "met", "rec", "Dinner with Leena Kivi")
e("2026-03-28", "kivi-family-office", "signed", "rec", "Kivi Family Office signed as co-investor alongside the buyer in the Harju transaction")
e("2026-09-02", "kivi-family-office", "wrote", "imsg", "Johan texts Leena about Project Birch", opp="birch")
e("2026-09-03", "kivi-family-office", "asked_info", "imsg", "Leena: interested, send the teaser", opp="birch")
e("2026-07-09", "fjell-capital", "wrote", "mail", "Sofia sends Magnus the Project Birch teaser", opp="birch")
e("2026-07-12", "fjell-capital", "replied", "mail", "Magnus replies: Fjell passes on Birch, it is not our sector, but please keep us on your list for industrials", opp="birch")
e("2026-07-12", "fjell-capital", "declined", "same", "Magnus passes on Birch (not our sector) but asks to stay on the list for industrials", opp="birch")
e("2026-08-02", "mikael-rautio", "asked_info", "imsg", "Mikael asks by text what minority stakes are coming up this autumn")
e("2026-09-25", "mikael-rautio", "committed", "imsg", "Mikael: count me in for 100k if a minority round comes up")

# What the mail and texts actually say, in the sender's words. Keyed by (date, party, event).
SAID = {
    ("2026-06-30", "vaara-packaging", "outcome"): "Johan,\n\nThe money landed this morning and the deal is closed. Thank you, and Sofia too, for getting us there. Dinner is on me in August.\n\nAntti",
    ("2026-08-17", "harju-logistics", "reordered"): "Hi Johan,\n\nWe want to go ahead with the Lempäälä acquisition and we want you to run it, same terms as last time. Signed engagement letter attached.\n\nPetra",
    ("2026-09-21", "harju-logistics", "referred"): "Johan, meet Jari Tammela (cc). Jari is thinking about succession at Tammela Steel and I told him you are the people to talk to. Jari, Johan ran our sale last spring.\n\nPetra",
    ("2026-09-22", "tammela-steel", "asked"): "Thanks Petra. Johan, could we meet in Hämeenlinna in the next couple of weeks?\n\nJari",
    ("2026-06-04", "kallio-foods", "asked_proposal"): "Johan,\n\nThe board met yesterday. Could you send us a proposal for running the sale of a majority stake? Fees, timeline, team.\n\nMari",
    ("2026-06-10", "kallio-foods", "wrote"): "Mari,\n\nOur proposal for Project Birch is attached: a retainer of EUR 8,000 a month and a success fee. Happy to walk the board through it.\n\nJohan",
    ("2026-06-16", "kallio-foods", "signed"): "Signed engagement letter attached. Let's get going.\n\nMari",
    ("2026-07-01", "kallio-foods", "paid"): "Hi Johan, the first monthly retainer (EUR 8,000) went out today. Best, Lauri Niemi, CFO, on behalf of Mari",
    ("2026-08-20", "elina-saari", "introduced"): "Johan, let me introduce Camilla Nord (cc), CEO of Nordvent Systems. Camilla is starting to think about an exit and I suggested she talk to you. Camilla, Johan is the corporate-finance adviser I mentioned.\n\nElina",
    ("2026-08-21", "nordvent-systems", "replied"): "Thank you Elina. Johan, nice to meet you. Would next Thursday work for a first conversation?\n\nCamilla",
    ("2026-09-15", "nordvent-systems", "asked_info"): "Johan,\n\nThanks for the meeting. Before we go further: how would you run a sale process for a company our size, and roughly what would it cost us?\n\nCamilla",
    ("2026-09-24", "merikoski-bank", "introduced"): "Sofia, as agreed under our referral arrangement: Sanna Okko (cc) of Okko Instruments is looking at selling the company. Over to you.\n\nTuomas Leino, Merikoski Bank",
    ("2026-09-25", "okko-instruments", "replied"): "Thanks Tuomas. Sofia, glad to be connected.\n\nSanna",
    ("2026-09-28", "okko-instruments", "asked_proposal"): "Sofia, could you send a proposal for running the sale? We'd like to decide before November.\n\nSanna",
    ("2026-09-05", "lumo-health", "asked"): "Hello,\n\nI read your piece on selling a founder-owned company and it described our situation almost exactly. Could we have a call with one of the partners?\n\nVille Kuosmanen, Lumo Health",
    ("2026-09-08", "brannvik-marine", "asked_info"): "Johan, thanks for the Q3 letter. What multiples are you seeing for marine services companies right now? Asking for myself.\n\nErik",
    ("2026-09-18", "oravala-software", "replied"): "Good to meet you at the forum. Not this year, but let's talk again in January.\n\nPetteri",
    ("2026-07-08", "revontuli-growth", "asked_info"): "Sofia, could you send over the teaser for Project Birch?\n\nHenrik",
    ("2026-07-14", "revontuli-growth", "signed_nda"): "Signed NDA attached. Looking forward to the information memorandum.\n\nHenrik",
    ("2026-08-20", "revontuli-growth", "asked"): "Can you set up a management meeting with Kallio for us? Any day week 36",
    ("2026-09-10", "revontuli-growth", "bid"): "Sofia,\n\nPlease find attached Revontuli's non-binding indicative offer for Project Birch, subject to due diligence and our investment committee.\n\nHenrik",
    ("2026-09-02", "kivi-family-office", "wrote"): "Leena, we have a food company coming to market this autumn. Majority stake. Interested in a look?",
    ("2026-09-03", "kivi-family-office", "asked_info"): "Yes, send me the teaser",
    ("2026-07-09", "fjell-capital", "wrote"): "Magnus,\n\nThe teaser for Project Birch, a Finnish food producer, is attached. NDA on request.\n\nSofia",
    ("2026-07-12", "fjell-capital", "replied"): "Sofia, thanks, but we'll pass on this one, food is not our sector. Do keep us on your list for industrials.\n\nMagnus",
    ("2026-08-02", "mikael-rautio", "asked_info"): "Johan, anything with a minority stake coming up this autumn? I have some cash to put to work",
    ("2026-09-25", "mikael-rautio", "committed"): "Count me in for 100k if that minority round happens",
}


# Prospect-list rows with no dated interaction (ring 0, identified).
LIST_ONLY = ["pohjoisranta-dental", "nordic-pension-mutual", "strom-holding"]

# Labels the seller keeps. Not events: the scan must not turn these into rings.
STAGE = {
    "vaara-packaging": ("Mandates", "Closed", "won", "2026-06-30"),
    "harju-logistics": ("Mandates", "Mandate signed", "open", None),  # the add-on
    "tammela-steel": ("Mandates", "Contact made", "open", None),
    "kallio-foods": ("Mandates", "In market", "open", None),
    "vesi-analytics": ("Mandates", "Proposal made", "lost", "2026-04-30"),
    "nordvent-systems": ("Mandates", "Proposal made", "open", None),
    "okko-instruments": ("Mandates", "Lead in", "open", None),
    "lumo-health": ("Mandates", "Contact made", "open", None),
    "oravala-software": ("Mandates", "Lead in", "open", None),
    "pohjoisranta-dental": ("Mandates", "Contact made", "open", None),
    "revontuli-growth": ("Project Birch investors", "Indicative offer", "open", None),
    "kivi-family-office": ("Project Birch investors", "Teaser sent", "open", None),
    "fjell-capital": ("Project Birch investors", "Teaser sent", "lost", "2026-07-12"),
    "nordic-pension-mutual": ("Investor relations", "Long list", "open", None),
    "strom-holding": ("Investor relations", "Long list", "open", None),
    "mikael-rautio": ("Investor relations", "Warm", "open", None),
    "merikoski-bank": ("Partners", "Agreement signed", "open", None),
}
CREATED = {s: "2026-01-15" for s in STAGE}  # when Johan imported his old spreadsheet; not an event
CREATED.update({"tammela-steel": "2026-09-22", "nordvent-systems": "2026-08-21", "okko-instruments": "2026-09-25",
                "lumo-health": "2026-09-05", "oravala-software": "2026-09-18", "kallio-foods": "2026-05-12"})


# --- helpers ------------------------------------------------------------------------------------------

def reset(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)


def human(date):
    return date.strftime("%b %d, %Y")


# --- shared exports: mail, calendar, iMessage, the newsletter ------------------------------------------

def emit_shared():
    root = os.path.join(HERE, "shared")
    reset(root)
    n = 0
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//made-up//lindgate deal-maker fixture//EN",
           "X-WR-CALNAME:Johan Aalto (with Sofia's shared calendar)"]
    threads = {}
    news = [["date", "email", "name", "company", "event", "campaign"]]
    for ev in sorted(EV, key=lambda x: x["date"]):
        if ev["src"] in ("rec", "same"):  # same: the previous line's message says it too
            continue
        assert ev["date"] >= WINDOW_START, ev
        name, addr = contact(ev["party"])
        me_name, me = TEAM[ev["owner"]]
        date = ev["date"].isoformat()
        if ev["src"] == "mail":
            n += 1
            mid = f"<lg{n:04d}.{ev['date'].strftime('%Y%m%d')}@mail.example>"
            ours = ev["event"] == "wrote"
            frm, to = (f"{me_name} <{me}>", f"{name} <{addr}>") if ours else (f"{name} <{addr}>", f"{me_name} <{me}>")
            cc = ""
            if ev["via"]:
                vname, vaddr = contact(ev["via"])
                cc = f"Cc: {vname} <{vaddr}>\n"
            if ev["event"] in ("introduced", "referred"):
                target = {"elina-saari": "nordvent-systems", "merikoski-bank": "okko-instruments",
                          "harju-logistics": "tammela-steel"}[ev["party"]]
                tname, taddr = contact(target)
                cc = f"Cc: {tname} <{taddr}>\n"
            subject = {"birch": "Project Birch"}.get(ev["opp"], FIRM if not ev["via"] else "Introduction")
            body = SAID[(date, ev["party"], ev["event"])]
            write(os.path.join(root, "mail", f"{date}-lg{n:04d}.eml"),
                  f"From: {frm}\nTo: {to}\n{cc}Date: {date}T09:00:00Z\nMessage-ID: {mid}\nSubject: {subject}\n\n{body}\n")
        elif ev["src"] == "cal":
            n += 1
            ics += ["BEGIN:VEVENT", f"UID:lg{n:04d}@lindgate.example", f"DTSTART:{date.replace('-', '')}T100000Z",
                    f"DTEND:{date.replace('-', '')}T110000Z", f"SUMMARY:{ev['what']}",
                    f"ATTENDEE;CN={name}:mailto:{addr}", f"ORGANIZER;CN={me_name}:mailto:{me}", "END:VEVENT"]
        elif ev["src"] == "imsg":
            ours = ev["event"] == "wrote"
            stamp = f"{human(ev['date'])}  {'8:14:02 PM' if ours else '9:02:40 AM'}"
            threads.setdefault(addr, []).append(f"{stamp}\n{'Me' if ours else addr}\n{SAID[(date, ev['party'], ev['event'])]}\n")
        elif ev["src"] == "news":
            news.append([date, addr, name, P[ev["party"]]["name"], ev["event"],
                         "Q3 letter" if ev["event"] == "opened" else ""])
    # Noise a real export has: the firm's own meetings, a sponsor invoice, a vendor.
    for date, summary in [("2026-06-08", "Partners' weekly"), ("2026-07-06", "Partners' weekly"),
                          ("2026-09-14", "Partners' weekly"), ("2026-09-16", "Nordic Mid-Market Forum (Lindgate sponsors a table)")]:
        n += 1
        ics += ["BEGIN:VEVENT", f"UID:lg{n:04d}@lindgate.example", f"DTSTART:{date.replace('-', '')}T080000Z",
                f"SUMMARY:{summary}", f"ORGANIZER;CN=Johan Aalto:mailto:{TEAM['johan'][1]}", "END:VEVENT"]
    for date, frm, subj, body in [
        ("2026-08-05", "Nordic Mid-Market Forum <billing@nmmf.example>", "Invoice: table sponsorship, 16-17 Sep",
         "Thank you for sponsoring a table at the Nordic Mid-Market Forum. Invoice NMMF-2208, EUR 4,500, attached."),
        ("2026-09-01", "Sofia Berglund <sofia@lindgate.example>", "Birch long list",
         "Johan, I've sent the teaser to Revontuli and Fjell. Kivi is yours. I'll update the sheet."),
        ("2026-09-30", "DataRoom Pro <noreply@dataroom.example>", "Your monthly data room usage",
         "Project Birch: 14 active users this month."),
    ]:
        n += 1
        write(os.path.join(root, "mail", f"{date}-lg{n:04d}.eml"),
              f"From: {frm}\nTo: Johan Aalto <{TEAM['johan'][1]}>\nDate: {date}T07:00:00Z\n"
              f"Message-ID: <lg{n:04d}@mail.example>\nSubject: {subj}\n\n{body}\n")
    ics.append("END:VCALENDAR")
    write(os.path.join(root, "calendar.ics"), "\n".join(ics) + "\n")
    for handle, msgs in threads.items():
        write(os.path.join(root, "imessage", f"{handle}.txt"), "\n".join(msgs))
    write_csv(os.path.join(root, "newsletter-activity.csv"), news)
    write(os.path.join(root, "analytics-summary.md"),
          "# lindgate.example, last 28 days (read 2026-10-09)\n\n"
          "- Visitors: 412 (Plausible)\n"
          "- 'Selling a founder-owned company' (article): 183 views, 9 visits to the contact page from it\n"
          "- The quarterly letter: 214 subscribers; the Q3 issue was opened by 121 (newsletter platform report)\n")


# --- variant A: a Pipedrive-style CSV export ----------------------------------------------------------

def emit_crm():
    root = os.path.join(HERE, "crm", "pipedrive-export-2026-10-09")
    reset(os.path.join(HERE, "crm"))
    owner_name = lambda s: TEAM[P[s]["owner"]][0]
    orgs = [["Organization - ID", "Organization - Name", "Organization - Address", "Organization - Owner",
             "Organization - Label"]]
    persons = [["Person - ID", "Person - Name", "Person - Organization", "Person - Email", "Person - Owner",
                "Person - Label"]]
    org_id, person_id = {}, {}
    for i, (s, p) in enumerate(sorted(P.items()), start=1):
        if p["type"] == "organisation":
            org_id[s] = 100 + i
            label = {"investor": "Investor", "partner": "Partner", "customer": "Prospect"}[p["kind"]]
            orgs.append([org_id[s], p["name"], p["city"], owner_name(s), label])
        name, addr = contact(s)
        person_id[s] = 500 + i
        persons.append([person_id[s], name, p["name"] if p["type"] == "organisation" else (p["org"] or ""),
                        addr, owner_name(s), "Investor" if p["kind"] == "investor" else ""])
    deals = [["Deal - ID", "Deal - Title", "Deal - Organization", "Deal - Contact person", "Deal - Value",
              "Deal - Currency", "Deal - Pipeline", "Deal - Stage", "Deal - Status", "Deal - Owner",
              "Deal - Deal created", "Deal - Won time", "Deal - Lost time", "Deal - Lost reason"]]
    deal_id = {}
    titles = {"vaara-packaging": "Sale of Vaara Packaging", "harju-logistics": "Harju add-on acquisition",
              "kallio-foods": "Project Birch (sale of Kallio Foods)", "vesi-analytics": "Vesi minority raise",
              "revontuli-growth": "Birch - Revontuli", "kivi-family-office": "Birch - Kivi", "fjell-capital": "Birch - Fjell",
              "merikoski-bank": "Merikoski referral agreement"}
    values = {"vaara-packaging": 420000, "harju-logistics": 150000, "kallio-foods": 600000, "vesi-analytics": 80000}
    for i, (s, (pipe, stage, status, closed)) in enumerate(sorted(STAGE.items()), start=1):
        deal_id[s] = 900 + i
        name, _ = contact(s)
        deals.append([deal_id[s], titles.get(s, P[s]["name"]), P[s]["name"] if P[s]["type"] == "organisation" else "",
                      name, values.get(s, ""), "EUR" if s in values else "", pipe, stage, status, owner_name(s),
                      CREATED[s], closed if status == "won" else "", closed if status == "lost" else "",
                      "Timing: revisit after 2026 accounts" if s == "vesi-analytics" else
                      ("Not our sector (keep for industrials)" if s == "fjell-capital" else "")])
    # A second Harju deal: the sale itself, won in March.
    deals.append([999, "Sale of Harju Logistics (majority)", P["harju-logistics"]["name"], "Petra Harju", 380000,
                  "EUR", "Mandates", "Closed", "won", "Johan Aalto", "2025-09-04", "2026-03-31", "", ""])
    acts = [["Activity - ID", "Activity - Type", "Activity - Subject", "Activity - Due date", "Activity - Done",
             "Activity - Deal", "Activity - Person", "Activity - Organization", "Activity - Note",
             "Activity - Assigned to user"]]
    # The CRM holds what it has always held: every older event, and the in-window meetings Johan logged.
    a = 3000
    for ev in sorted(EV, key=lambda x: x["date"]):
        logged = ev["src"] == "rec" or (ev["src"] == "cal")
        if not logged:
            continue
        a += 1
        s = ev["party"]
        typ = "Meeting" if ev["event"] == "met" or ev["src"] == "cal" else "Task"
        subj = ev["what"].split(";")[0]
        deal = deal_id.get(s, "")
        if s == "harju-logistics" and ev["date"] < dt.date(2026, 4, 1):
            deal = 999
        acts.append([a, typ, subj, ev["date"].isoformat(), "Done", deal, contact(s)[0],
                     P[s]["name"] if P[s]["type"] == "organisation" else (P[s]["org"] or ""), ev["what"] + ".",
                     TEAM[ev["owner"]][0]])
    # An open task, which is a plan, not an event.
    a += 1
    acts.append([a, "Call", "Follow up on the proposal", "2026-10-14", "To do", deal_id["nordvent-systems"],
                 "Camilla Nord", P["nordvent-systems"]["name"], "", "Johan Aalto"])
    write_csv(os.path.join(root, "organizations.csv"), orgs)
    write_csv(os.path.join(root, "persons.csv"), persons)
    write_csv(os.path.join(root, "deals.csv"), deals)
    write_csv(os.path.join(root, "activities.csv"), acts)


# --- variant B: a shared folder used as the CRM -------------------------------------------------------

def emit_folder():
    root = os.path.join(HERE, "folder", "Lindgate Deals")
    reset(os.path.join(HERE, "folder"))
    company_rows = [["Company", "Contact", "Email", "City", "Status", "Owner", "Last contact", "Next step", "Notes"]]
    investor_rows = [["Investor", "Contact", "Email", "City", "Status", "Owner", "Last contact", "Ticket (EUR)", "Notes"]]
    last = {}
    for ev in EV:
        last[ev["party"]] = max(last.get(ev["party"], ev["date"]), ev["date"])
    status = {s: STAGE.get(s, ("", "", "", ""))[1] for s in P}
    status["harju-logistics"] = "Closed (sale); add-on mandate signed"
    nexts = {"nordvent-systems": "Send proposal", "okko-instruments": "Proposal by 15 Oct", "tammela-steel": "Second meeting",
             "lumo-health": "Ask about timing", "kallio-foods": "Final offers 31 Oct", "revontuli-growth": "Mgmt meeting",
             "kivi-family-office": "Send teaser", "oravala-software": "Call in January"}
    for s, p in sorted(P.items()):
        name, addr = contact(s)
        lc = last[s].isoformat() if s in last else ""
        row = [p["name"], name, addr, p["city"], status[s], p["owner"].title(), lc]
        if p["kind"] == "investor":
            investor_rows.append(row + [{"revontuli-growth": "20-40m", "kivi-family-office": "2-5m", "mikael-rautio": "0.1m",
                                         "fjell-capital": "30-60m", "nordic-pension-mutual": "50m+",
                                         "strom-holding": "1-3m"}.get(s, ""), ""])
        else:
            company_rows.append(row + [nexts.get(s, ""), "Partner" if p["kind"] == "partner" else ""])
    write_csv(os.path.join(root, "Prospects - Companies.csv"), company_rows)
    write_csv(os.path.join(root, "Prospects - Investors.csv"), investor_rows)
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Companies"
    for r in company_rows:
        ws.append(r)
    ws2 = wb.create_sheet("Investors")
    for r in investor_rows:
        ws2.append(r)
    wb.save(os.path.join(root, "Prospects.xlsx"))
    # OneNote export: a page per meeting (in-window ones too, as Johan writes them up), and a page per
    # company with the dated things that were not meetings.
    logs = {}
    for ev in sorted(EV, key=lambda x: x["date"]):
        s = ev["party"]
        name, _ = contact(s)
        if ev["event"] == "met":
            date = ev["date"].isoformat()
            write(os.path.join(root, "Meeting notes", f"{date} {P[s]['name']}.md"),
                  f"# {P[s]['name']}: meeting\n\n{human(ev['date'])}\n\nPresent: {name}, "
                  f"{TEAM[ev['owner']][0]}\n\n- {ev['what']}.\n")
        elif ev["src"] == "rec":
            logs.setdefault(s, []).append(f"- {ev['date'].isoformat()}: {ev['what']}.")
    for s, lines in logs.items():
        write(os.path.join(root, "Companies", f"{P[s]['name']}.md"),
              f"# {P[s]['name']}\n\nContact: {contact(s)[0]}\n\n" + "\n".join(lines) + "\n")


# --- the truth, and the answer key --------------------------------------------------------------------

MOVES_NOTHING = {"wrote", "called", "posted", "declined", "unsubscribed", "note", None}


def emit_truth():
    truth = {MAP: {}}
    for s, p in P.items():
        evs = [[ev["date"].isoformat(), ev["event"]] for ev in sorted(EV, key=lambda x: x["date"])
               if ev["party"] == s and ev["event"] not in MOVES_NOTHING]
        if not evs:
            assert s in LIST_ONLY, s
            evs = [[TODAY.isoformat(), "identified"]]
        truth[MAP][p["name"]] = {"events": evs, "sector": p["sector"], "kind": p["kind"],
                                 "not_now": p["not_now"], "no": p["no"]}
    with open(os.path.join(HERE, "truth.json"), "w") as f:
        json.dump(truth, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    return truth


RING = ["Unaware", "Touched", "Engaged", "Considering", "Invested", "Started", "Returning", "Successful",
        "Ambassador"]
RING_OF = {}
for i, words in enumerate([["identified"], ["visited", "read", "viewed", "saw_ad", "clicked_ad", "opened"],
                           ["replied", "commented", "reacted", "followed", "subscribed", "downloaded", "signed_up", "joined", "met"],
                           ["asked", "asked_info", "asked_demo", "asked_trial", "asked_proposal", "asked_price", "joined_presale"],
                           ["accepted_terms", "committed_time", "introduced", "signed", "paid", "signed_nda", "bid", "committed"],
                           ["set_up", "onboarded", "first_use"], ["repeat_use", "renewed", "reordered", "reinvested"],
                           ["outcome", "expanded"], ["testimonial", "review", "case_study", "referred", "recommended"]]):
    for w in words:
        RING_OF[w] = i


def expected_ring(evs):
    best = 0
    for date, ev in evs:
        r = RING_OF[ev]
        if r == 6 and (TODAY - dt.date.fromisoformat(date)).days > 90:
            continue
        best = max(best, r)
    return best


def emit_answer_key(truth):
    src_name = {"same": "mail", "mail": "mail", "cal": "calendar", "imsg": "iMessage", "news": "newsletter export",
                "rec": "CRM / folder only"}
    out = [f"# Answer key: {FIRM} (deal-maker fixture)", "",
           f"Generated by `generate.py`; do not edit by hand. As of {TODAY}. One map, `{MAP}`. Rings are what the",
           "core computes from the events the sources show (a scorer recomputes them with the map engine, so this table",
           "is for people). Everything is invented.", "",
           "| Party | Kind | Sector | Ring | Why | Sources it needs |", "|---|---|---|---|---|---|"]
    for s, p in sorted(P.items(), key=lambda kv: (-expected_ring(truth[MAP][kv[1]["name"]]["events"]), kv[0])):
        r = expected_ring(truth[MAP][p["name"]]["events"])
        srcs = sorted({src_name[ev["src"]] for ev in EV if ev["party"] == s} or {"prospect list only"})
        extra = (f" **not_now {p['not_now']}.**" if p["not_now"] else
                 " **A no to one deal: the deal is lost; the party is not silenced.**" if p["no"] == "deal" else "")
        out.append(f"| {p['name']} | {p['kind']} | {p['sector']} | {r} {RING[r]} | {p['why']}{extra} | {', '.join(srcs)} |")
    out += ["", "## Investor words", "",
            "An NDA is `signed_nda`, a non-binding offer `bid`, a soft commitment `committed` (all ring 4), investing",
            "again `reinvested` (ring 6, recent only). A partner's or investor's introduction is `introduced` (4), never",
            "`referred`. Added to the record format on 2026-10-09, after this fixture's first run.", ""]
    nowords = [ev for ev in EV if ev["event"] is None]
    out += [f"- No event word: {ev['date']} · {P[ev['party']]['name']}: {ev['what']}." for ev in nowords] or \
           ["Every dated step in the sources now has an event word."]
    out += ["", "## Traps a correct scan avoids", "",
            "- A CRM stage or a spreadsheet status (*Proposal made*, *Contact made*, *Indicative offer*) is the seller's",
            "  label, not an event. Nordvent's stage says *Proposal made*; no proposal is in any source.",
            "- *Deal created* and *Last contact* dates are bookkeeping, not events.",
            "- Fjell's no is about Project Birch, not about Lindgate: it belongs on the Birch deal (`status: lost`), and",
            "  a map-wide `not_now` would silence Fjell for the industrials deals they asked to hear about.",
            "- A deal file that lists Kallio and its bidders would hand Kallio's `set_up` and `paid` to every bidder",
            " . A bidder's track is its own opportunity with `part_of:` the mandate.",
            "- Vesi, Vaara's mandate, Harju's sale and Kivi's co-investment are older than the mail export: only the",
            "  CRM or the folder places them.", ""]
    write(os.path.join(HERE, "ANSWER-KEY.md"), "\n".join(out))


if __name__ == "__main__":
    emit_shared()
    emit_crm()
    emit_folder()
    emit_answer_key(emit_truth())
    print("wrote shared/, crm/, folder/, truth.json and ANSWER-KEY.md in", HERE)
