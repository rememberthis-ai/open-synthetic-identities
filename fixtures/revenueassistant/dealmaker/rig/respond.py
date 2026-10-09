#!/usr/bin/env python3
"""Johan Aalto's answer to a card: respond.py <slug> <question text> -> prints the answer, or nothing.

The pattern -> answer table for The Revenue Assistant's (https://therevenueassistant.com) test rig: whole phrasings, specific rules first, nothing printed when no rule
matches (the driver then leaves the card for a person). The persona is ../PERSONA.md; keep the two together.
`RA_VARIANT=crm` answers the CRM question with Pipedrive; anything else, with the shared folder.
"""
import os
import re
import sys

CRM = os.environ.get("RA_VARIANT") == "crm"
q = sys.argv[2] if len(sys.argv) > 2 else ""

rules = [
    # Decisions about specific parties, before the generic questions.
    (r"(?i)fjell.*(do not contact|never|stop|remove)", "No, only not for food. Keep them for industrials."),
    (r"(?i)fjell", "They passed on this one. Keep them for industrials."),
    (r"(?i)vesi", "They said after the accounts. March."),
    (r"(?i)revontuli.*(offer|bid|commit)", "No. Non-binding. It means they are serious, nothing more."),
    (r"(?i)(rautio|mikael).*(100|commit|count)", "Mikael says that every autumn. Believe it when the money arrives."),
    (r"(?i)merikoski", "A partner. They get a fee share."),
    (r"(?i)(customer|client), (an )?investor,? or (a )?partner", "Ask me one at a time, with the name."),
    # Drafts.
    (r"(?i)(draft|message|email|mail).*(investor|revontuli|kivi|fjell|rautio|teaser)", "Who else has seen the teaser? Project name only, never the company. Then OK, from my mail."),
    (r"(?i)(send|approve|ok to send|right to send|does this read)", "Too American. Shorter. Then OK, send it from my mail."),
    # First run.
    (r"(?i)what (do you|you) offer|what is it|where does it stand|tell me (about|what)", "Corporate-finance advice. We sell founder-owned companies, Nordic, 5 to 50 million revenue. Two live mandates, two sales closed this year."),
    (r"(?i)who (is it|it is) for|counterpart|who are (they|your)", "Owners who want to sell. And the investors who buy: funds, family offices, a few private people. The investors matter more than you would think."),
    (r"(?i)web ?site|brand|deck|link", "lindgate.example. There is an article on selling a family company, people read it."),
    (r"(?i)what has worked|what worked|brought (you|people)", "Our own network. Lawyers and one bank send us clients. The quarterly letter a little."),
    (r"(?i)(forum|event|sponsor|september)", "We paid for a table at the Nordic Mid-Market Forum. One good conversation."),
    (r"(?i)who else|team|colleague|partner(s)? (in|at) the firm", "Sofia Berglund, my partner. She has the bank and most of the funds."),
    (r"(?i)\bcrm\b|folder|spreadsheet|excel|where (do|are) (you keep|your deals)",
     "Pipedrive since January. The stages are not up to date." if CRM else "No CRM. Excel and OneNote, in the shared folder."),
    (r"(?i)messages|imessage|whatsapp|texts", "Yes, but only work threads. My phone has my family on it."),
    (r"(?i)mail|calendar|inbox", "Yes. Mine and Sofia's."),
    (r"(?i)market|how many (companies|people)|ring 0", "Maybe 2,000 companies that size in the Nordics who could sell in the next five years. And 300 or so investors."),
    (r"(?i)analytics|search console|ads|advert", "Sofia set up something for the site. I don't know what. No ads."),
    (r"(?i)repo|code|engineer", "We are advisers. There is no code."),
    (r"(?i)maturity|repeatable|ad.hoc", "Team is repeatable. The letter is more ad hoc than you think. Referrals are repeatable because of the bank agreement."),
    (r"(?i)family|health|politic", "Not relevant."),
]

for pattern, answer in rules:
    if re.search(pattern, q):
        print(answer)
        break
