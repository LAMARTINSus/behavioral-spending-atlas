
import sqlite3, json, os, uuid
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bsa-dev-secret")

DB_PATH = os.path.join(os.path.dirname(__file__), "bsa.db")

QUESTIONS = [{"id": 1, "section": "Decision Mechanics", "text": "When buying something non-essential, such as clothing, electronics, or a home upgrade, what do you focus on first?", "options": {"A": "Finding an option that costs less and feels financially safe.", "B": "Finding an option that is reliable and likely to perform well over time.", "C": "Choosing something that feels right and enjoyable to use.", "D": "Noticing what brands, trends, or people you trust are choosing."}}, {"id": 2, "section": "Decision Mechanics", "text": "You are choosing between two similar products. One is less expensive. The other is clearly better built and likely to last longer. What do you usually do?", "options": {"A": "Choose the less expensive option.", "B": "Choose the better-built option if the extra cost seems justified.", "C": "Go back and forth before deciding.", "D": "Choose based on style, brand, or how it reflects you."}}, {"id": 3, "section": "Decision Mechanics", "text": "When buying something moderately important, such as shoes, headphones, or a small appliance, how do you usually decide?", "options": {"A": "I compare options to avoid overspending.", "B": "I compare options to find the strongest quality and performance.", "C": "I decide when something feels right.", "D": "I decide quickly if it matches my taste or preferences."}}, {"id": 4, "section": "Decision Mechanics", "text": "When a purchase decision takes longer than expected, what bothers you the most?", "options": {"A": "The possibility of paying more than necessary.", "B": "The time and mental energy the decision is consuming.", "C": "The uncertainty of whether I am making the right choice.", "D": "The concern that I might miss a better or more fitting option."}}, {"id": 5, "section": "Decision Mechanics", "text": "When you see a discount or promotion on something you were already considering, how do you typically respond?", "options": {"A": "It strongly increases the chance that I choose it.", "B": "It gets my attention, but I still evaluate quality carefully.", "C": "It creates excitement and increases my desire to buy.", "D": "It matters more if the brand or product already fits my preferences."}}, {"id": 6, "section": "Decision Mechanics", "text": "After making a purchase, which thought is most familiar to you?", "options": {"A": "I hope this was a financially smart decision.", "B": "I hope this performs well and meets expectations.", "C": "I\u2019m glad I chose this. It feels right.", "D": "This reflects my taste or where I want to be."}}, {"id": 7, "section": "Decision Mechanics", "text": "When you hesitate before buying something, what is usually behind that hesitation?", "options": {"A": "Concern about spending too much.", "B": "Concern about quality or performance.", "C": "Uncertainty about how I feel about it.", "D": "Uncertainty about whether it fits me or my standards."}}, {"id": 8, "section": "Decision Mechanics", "text": "When something costs more but appears better, how do you usually respond?", "options": {"A": "I usually prefer to stay with the less expensive option.", "B": "I consider whether the performance justifies the extra cost.", "C": "I feel tempted, but I\u2019m not always sure.", "D": "I\u2019m more interested if it elevates the experience or image."}}, {"id": 9, "section": "Decision Mechanics", "text": "When making a quick purchase, what do you tend to prioritize most?", "options": {"A": "Cost.", "B": "Reliability.", "C": "What feels right in the moment.", "D": "Familiarity, taste, or preference."}}, {"id": 10, "section": "Decision Mechanics", "text": "What defines a good purchase decision for you?", "options": {"A": "Spending wisely.", "B": "Getting something that works well.", "C": "Feeling satisfied with the choice.", "D": "Choosing something that expresses who I am."}}, {"id": 11, "section": "Core Drivers", "text": "What makes a purchase satisfying to you?", "options": {"A": "It was financially efficient.", "B": "It performs well.", "C": "It feels good.", "D": "It reflects my identity."}}, {"id": 12, "section": "Core Drivers", "text": "When you see something you did not plan to buy but it catches your attention, what usually happens next?", "options": {"A": "I ignore it and move on.", "B": "I pause and evaluate whether it adds real value.", "C": "I feel drawn to it and seriously consider it.", "D": "I imagine myself owning it and how it would fit my life."}}, {"id": 13, "section": "Core Drivers", "text": "How much do brands influence your decision-making?", "options": {"A": "Very little.", "B": "Somewhat.", "C": "It depends on the category.", "D": "Strongly."}}, {"id": 14, "section": "Core Drivers", "text": "When buying something visible to others, such as clothing, a car, or a phone, what matters most?", "options": {"A": "Practical function.", "B": "Performance and quality.", "C": "Personal enjoyment.", "D": "Image and perception."}}, {"id": 15, "section": "Core Drivers", "text": "When you decide to upgrade something, such as a phone, car, or home item, what must be true for it to feel justified?", "options": {"A": "It makes financial sense.", "B": "It clearly improves performance or usefulness.", "C": "It feels exciting and enjoyable.", "D": "It represents progress or a higher level."}}, {"id": 16, "section": "Core Drivers", "text": "When you like something expensive, what are you most likely to do?", "options": {"A": "Usually not buy it.", "B": "Evaluate it carefully first.", "C": "Sometimes go for it if the feeling is strong enough.", "D": "Buy it if it strongly fits my taste or identity."}}, {"id": 17, "section": "Core Drivers", "text": "When making most spending decisions, what influences you the most?", "options": {"A": "Financial logic.", "B": "Performance and function.", "C": "Emotional response.", "D": "Identity alignment."}}, {"id": 18, "section": "Core Drivers", "text": "If an option costs more but clearly saves time or effort, such as hiring help, using a faster tool, or paying for convenience, how do you usually respond?", "options": {"A": "I prefer the less expensive option, even if it requires more effort.", "B": "It depends on whether the time saved is truly meaningful.", "C": "I often choose the option that makes life easier.", "D": "I strongly prefer options that simplify life and create a smoother experience."}}, {"id": 19, "section": "Core Drivers", "text": "When something feels right to you, what usually makes it feel right?", "options": {"A": "It makes financial sense.", "B": "It seems likely to perform well.", "C": "It feels good emotionally.", "D": "It fits my identity, taste, or standards."}}, {"id": 20, "section": "Core Drivers", "text": "When comparing options, what naturally pulls your attention the most?", "options": {"A": "Price.", "B": "Quality and function.", "C": "How I feel about it.", "D": "Brand, style, or image."}}, {"id": 21, "section": "Behavior Over Time", "text": "How often do you buy unplanned items?", "options": {"A": "Rarely.", "B": "Occasionally, when it makes sense.", "C": "Often, when something catches my attention.", "D": "Frequently. I enjoy spontaneous decisions."}}, {"id": 22, "section": "Behavior Over Time", "text": "After making an unplanned purchase, what is your most common reaction?", "options": {"A": "I question whether it was necessary.", "B": "I evaluate whether it was actually useful.", "C": "I focus on whether it felt worth it emotionally.", "D": "I think about whether it fits my lifestyle or image."}}, {"id": 23, "section": "Behavior Over Time", "text": "If solving a problem requires either spending more money or spending more time, what do you usually choose?", "options": {"A": "Spend more time to save money.", "B": "Balance both depending on the situation.", "C": "Spend more money if it reduces effort.", "D": "Spend more money if it meaningfully improves the experience."}}, {"id": 24, "section": "Behavior Over Time", "text": "If you like something but it does not make practical sense, what do you usually do?", "options": {"A": "I usually don\u2019t buy it.", "B": "I hesitate and analyze it carefully.", "C": "I sometimes buy it if it feels right.", "D": "I buy it if it strongly reflects my taste or identity."}}, {"id": 25, "section": "Behavior Over Time", "text": "When many people recommend or choose something, what effect does that have on you?", "options": {"A": "It does not affect me much.", "B": "It makes me look closer, but I still decide independently.", "C": "It increases my interest.", "D": "It strongly influences my decision."}}, {"id": 26, "section": "Behavior Over Time", "text": "How often do you revisit a decision after already making it?", "options": {"A": "Rarely. I usually trust my decision.", "B": "Sometimes, if I\u2019m not fully sure.", "C": "Often. I like to double-check.", "D": "Very often. I want to be certain I chose correctly."}}, {"id": 27, "section": "Behavior Over Time", "text": "What tends to create the most tension for you during a purchase decision?", "options": {"A": "The risk of spending more than necessary.", "B": "The risk of choosing something that won\u2019t perform well.", "C": "The risk of not feeling satisfied with the choice.", "D": "The risk of choosing something that doesn\u2019t represent me well."}}, {"id": 28, "section": "Behavior Over Time", "text": "You are buying a pair of shoes. One option is less expensive and decent. The other is more expensive but clearly better built. What do you do?", "options": {"A": "Choose the less expensive option to stay efficient.", "B": "Choose the better-built option for long-term value.", "C": "Go back and forth before deciding.", "D": "Choose based on style, brand, or how it represents me."}}, {"id": 29, "section": "Behavior Over Time", "text": "You are choosing a hotel for a trip. One option is basic and lower-priced. The other is more expensive but offers a much better experience. What matters most?", "options": {"A": "Saving money.", "B": "Comfort and reliability.", "C": "How enjoyable the stay will feel.", "D": "Whether the experience feels elevated or aspirational."}}, {"id": 30, "section": "Behavior Over Time", "text": "You need a tool or service. One option takes more effort but costs less. The other costs more but saves time and effort. What do you usually choose?", "options": {"A": "Save money and accept the extra effort.", "B": "Decide based on how often I\u2019ll use it.", "C": "Choose convenience if it feels worth it.", "D": "Choose what makes life smoother and more elevated."}}, {"id": 31, "section": "Social Influence + FOMO", "text": "When you see others enjoying experiences online, such as travel, restaurants, or events, what usually happens inside you?", "options": {"A": "I observe it, but it does not change what I want.", "B": "I notice it, but stay focused on my own priorities.", "C": "I start thinking about doing something similar.", "D": "I feel a strong urge to change my plans or upgrade my situation."}}, {"id": 32, "section": "Social Influence + FOMO", "text": "When you compare your life to what you see online, how does it affect your decisions?", "options": {"A": "It has little to no effect on my decisions.", "B": "I notice it, but stay consistent with my priorities.", "C": "It makes me rethink what I want and explore options.", "D": "It makes me feel behind and pushes me to act."}}, {"id": 33, "section": "Social Influence + FOMO", "text": "After seeing something appealing on social media, such as a product, experience, or lifestyle, what are you most likely to do next?", "options": {"A": "Move on without taking any action.", "B": "Look it up briefly, but usually don\u2019t pursue it.", "C": "Research it and seriously consider it.", "D": "Take steps to get or experience something similar."}}, {"id": 34, "section": "Social Influence + FOMO", "text": "When you repeatedly see the same type of product or lifestyle online, what effect does it usually have on you?", "options": {"A": "No real effect.", "B": "I notice it, but don\u2019t act on it.", "C": "It increases my desire over time.", "D": "It makes me feel I should consider upgrading or changing something."}}, {"id": 35, "section": "Social Influence + FOMO", "text": "When you see friends or people you follow using or recommending something, how does it affect you?", "options": {"A": "It doesn\u2019t affect my interest.", "B": "I may look into it, but I still decide independently.", "C": "It increases my interest and makes me consider it.", "D": "It strongly influences me and makes me want to try it."}}, {"id": 36, "section": "Social Influence + FOMO", "text": "When you see others upgrading their lifestyle, home, style, or experiences, what usually happens?", "options": {"A": "It doesn\u2019t affect me.", "B": "I notice it, but mainly observe.", "C": "I compare and start reconsidering some of my own choices.", "D": "I feel motivated to improve my situation, even if it involves spending."}}, {"id": 37, "section": "Social Influence + FOMO", "text": "After seeing something appealing on social media, such as a product, experience, or lifestyle, what are you most likely to do next?", "options": {"A": "Move on without taking any action.", "B": "Look it up briefly, but usually don\u2019t pursue it further.", "C": "Spend time researching it and seriously consider it.", "D": "Actively plan or take steps to get or experience something similar."}}, {"id": 38, "section": "Social Influence + FOMO", "text": "When you see others enjoying experiences, such as travel, restaurants, or events, what usually happens internally?", "options": {"A": "I observe it, but it does not change what I want.", "B": "I feel mild interest, but stay focused on my own priorities.", "C": "I start thinking about doing something similar.", "D": "I feel a strong urge to change my plans or upgrade my situation."}}, {"id": 39, "section": "Social Influence + FOMO", "text": "When you notice others living a lifestyle that seems more exciting or elevated, how does it affect your decisions?", "options": {"A": "It does not influence my decisions.", "B": "It makes me reflect, but I stay consistent with my plans.", "C": "It makes me reconsider what I want and explore new options.", "D": "It pushes me to spend or change things to close that gap."}}, {"id": 40, "section": "Social Influence + FOMO", "text": "When you feel like you might be missing out compared to others, what do you typically do?", "options": {"A": "I recognize the feeling and let it pass without acting on it.", "B": "I think about it, but rarely change my behavior.", "C": "I adjust some of my plans or consider new options.", "D": "I take action to improve my situation, even if it involves spending."}}]
DIMENSIONS = ["VAL", "PERF", "EMO", "STA", "CON", "PLN", "REG", "INF", "EXP"]
ARCHETYPES = {"Value Optimizer": {"subtitle": "with a tendency to protect value and avoid obvious waste", "strengths": ["You naturally look for financially sound decisions.", "You tend to resist obvious overpaying and weak value.", "You usually think before acting."], "blind_spots": ["You may mistake the lower-cost option for the better overall choice.", "You can quietly underinvest in quality or long-term upside."], "prompt": "You often ask whether something is truly worth the cost before you ask whether you want it."}, "Performance Seeker": {"subtitle": "with a strong focus on reliability and outcomes", "strengths": ["You care about durability, quality, and long-term performance.", "You don\u2019t like weak solutions or things that fail quickly.", "You usually make thoughtful decisions."], "blind_spots": ["You can spend too much time searching for the best possible option.", "Your desire for the right answer can delay action."], "prompt": "You tend to buy for performance first and price second."}, "Emotional Spender": {"subtitle": "with choices strongly shaped by feeling", "strengths": ["You are open, responsive, and emotionally aware.", "You know when something feels meaningful or satisfying.", "You can make fast decisions."], "blind_spots": ["You may decide emotionally first and justify later.", "Your spending can shift with mood or immediate desire."], "prompt": "When something feels right emotionally, its pull can become stronger than logic."}, "Identity Curator": {"subtitle": "with purchases shaped by self-expression and image", "strengths": ["You have a strong sense of taste and alignment.", "You tend to choose things that feel personal and coherent.", "Your decisions often reflect standards, not randomness."], "blind_spots": ["You may assign too much meaning to visible or symbolic items.", "You can overpay for alignment or image."], "prompt": "You don\u2019t just choose what works. You choose what fits who you are or who you want to be."}, "Convenience Maximizer": {"subtitle": "with a strong bias toward ease and low friction", "strengths": ["You value time and energy, not just money.", "You are drawn to practical simplicity.", "You can move quickly when others get stuck."], "blind_spots": ["You may pay convenience premiums more often than you realize.", "You can use spending to avoid effort rather than to create real value."], "prompt": "You are highly sensitive to friction. If something makes life easier, its appeal rises quickly."}, "Over-Optimizer": {"subtitle": "with a tendency to keep evaluating after a decision is almost made", "strengths": ["You think carefully and rarely move blindly.", "You want decisions to be strong, not careless.", "You value clarity and control."], "blind_spots": ["You can overcompare and create unnecessary decision fatigue.", "You may keep searching after you already have enough information."], "prompt": "Your strongest decisions often get slowed down by the search for extra certainty."}, "Impulse Reactor": {"subtitle": "with fast response to appealing opportunities", "strengths": ["You can act quickly when something genuinely matters.", "You are open to possibilities and responsive to opportunity.", "You don\u2019t always get stuck in overthinking."], "blind_spots": ["You may act before fully evaluating long-term consequences.", "Your spending can shift unexpectedly when something grabs your attention."], "prompt": "When something catches you at the right moment, your action threshold drops quickly."}, "Regret Avoider": {"subtitle": "with strong sensitivity to making the wrong choice", "strengths": ["You care about making sound decisions.", "You naturally try to reduce errors and waste.", "You usually don\u2019t act carelessly."], "blind_spots": ["You may revisit decisions too often.", "You can confuse extra checking with extra accuracy."], "prompt": "A lot of your hesitation is not about desire. It is about trying to protect yourself from regret."}, "Socially Influenced Buyer": {"subtitle": "with decisions shaped by what others are doing", "strengths": ["You are socially aware and open to trusted input.", "You notice trends, recommendations, and cues quickly.", "You are responsive to what is happening around you."], "blind_spots": ["Your interest can rise simply because others are doing something.", "You may adopt desires that were not originally yours."], "prompt": "Exposure matters for you. What you see others doing can change what feels relevant or desirable."}, "Experience Chaser": {"subtitle": "with strong pull toward enjoyment, novelty, and lived experience", "strengths": ["You value enjoyment and meaningful experiences.", "You are motivated by life quality, not just practicality.", "You are open to opportunities that enrich life."], "blind_spots": ["You may underweight long-term financial impact.", "In the moment, the value of the experience can feel bigger than the cost."], "prompt": "You often prioritize what makes life feel fuller, richer, or more alive."}, "FOMO-Driven Upgrader": {"subtitle": "with comparison pressure influencing desire and action", "strengths": ["You are highly responsive to shifts in your environment.", "You notice quickly when others are enjoying or upgrading something.", "You are motivated by possibility and movement."], "blind_spots": ["What you see can quietly redefine what feels necessary.", "You may act to close a perceived gap that didn\u2019t matter before exposure."], "prompt": "Comparison doesn\u2019t just affect your mood. It can reshape your decisions."}, "Balanced Strategist": {"subtitle": "with a flexible, multi-factor approach to decisions", "strengths": ["You can weigh price, quality, emotion, and identity together.", "You tend to adapt to context instead of relying on only one driver.", "You have the potential for very strong decision quality."], "blind_spots": ["When several factors matter equally, you may slow down.", "Too much balance can become indecision."], "prompt": "You are capable of strong decisions because you see more than one side of a purchase."}}
BASE_MAP = {"A": {"VAL": 2, "PLN": 1, "REG": 1, "EMO": -1}, "B": {"PERF": 2, "PLN": 1, "VAL": 1}, "C": {"EMO": 2, "EXP": 1, "PLN": -1}, "D": {"STA": 2, "INF": 1, "EXP": 1}}
SECTION_MULTIPLIER = {"1": 1.2, "2": 1.2, "3": 1.2, "4": 1.2, "5": 1.2, "6": 1.2, "7": 1.2, "8": 1.2, "9": 1.2, "10": 1.2, "11": 1.0, "12": 1.0, "13": 1.0, "14": 1.0, "15": 1.0, "16": 1.0, "17": 1.0, "18": 1.0, "19": 1.0, "20": 1.0, "21": 1.3, "22": 1.3, "23": 1.3, "24": 1.3, "25": 1.3, "26": 1.3, "27": 1.3, "28": 1.3, "29": 1.3, "30": 1.3, "31": 1.5, "32": 1.5, "33": 1.5, "34": 1.5, "35": 1.5, "36": 1.5, "37": 1.5, "38": 1.5, "39": 1.5, "40": 1.5}

LABELS = {
    "VAL": "Value sensitivity",
    "PERF": "Performance focus",
    "EMO": "Emotional drive",
    "STA": "Identity / status",
    "CON": "Convenience / effort",
    "PLN": "Planning / control",
    "REG": "Regret sensitivity",
    "INF": "Social influence",
    "EXP": "Experience drive",
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        creator TEXT,
        answers_json TEXT,
        result_json TEXT,
        name TEXT,
        social_platform TEXT,
        social_handle TEXT,
        gender TEXT,
        age_range TEXT,
        email TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def extra_for_question(qid, ans):
    extra = {}
    if qid == 18 and ans in ("C","D"):
        extra["CON"] = extra.get("CON",0)+2
    if qid == 21:
        if ans == "C":
            extra["PLN"] = extra.get("PLN",0)-2
            extra["EMO"] = extra.get("EMO",0)+1
        elif ans == "D":
            extra["PLN"] = extra.get("PLN",0)-3
            extra["EMO"] = extra.get("EMO",0)+2
    if qid == 23:
        if ans == "A":
            extra["VAL"] = extra.get("VAL",0)+2
        elif ans in ("C","D"):
            extra["CON"] = extra.get("CON",0)+2
    if qid == 25:
        if ans == "C":
            extra["INF"] = extra.get("INF",0)+2
        elif ans == "D":
            extra["INF"] = extra.get("INF",0)+3
    if qid == 26 and ans in ("C","D"):
        extra["REG"] = extra.get("REG",0)+2
    if 31 <= qid <= 40:
        if ans == "A":
            extra["INF"] = extra.get("INF",0)-1
        elif ans == "B":
            extra["INF"] = extra.get("INF",0)+1
        elif ans == "C":
            extra["INF"] = extra.get("INF",0)+2
            extra["EMO"] = extra.get("EMO",0)+1
        elif ans == "D":
            extra["INF"] = extra.get("INF",0)+3
            extra["EMO"] = extra.get("EMO",0)+2
            extra["EXP"] = extra.get("EXP",0)+1
    return extra

def compute_scores(answers):
    scores = {d: 0 for d in DIMENSIONS}
    for q in QUESTIONS:
        qid = q["id"]
        ans = answers.get(str(qid))
        if not ans:
            continue
        mult = SECTION_MULTIPLIER[str(qid)] if isinstance(next(iter(SECTION_MULTIPLIER)), str) else SECTION_MULTIPLIER[qid]
        for dim, pts in BASE_MAP[ans].items():
            scores[dim] += pts * mult
        for dim, pts in extra_for_question(qid, ans).items():
            scores[dim] += pts * mult
    return scores

def contradictions(answers):
    flags = []
    # planning vs impulse
    q3 = answers.get("3")
    q21 = answers.get("21")
    if q3 in ("A","B") and q21 in ("C","D"):
        flags.append("planning_vs_impulse")
    # social independence vs social influence
    q13 = answers.get("13")
    q35 = answers.get("35")
    if q13 == "A" and q35 in ("C","D"):
        flags.append("brand_social_conflict")
    # value vs experience
    q1 = answers.get("1")
    q29 = answers.get("29")
    if q1 == "A" and q29 in ("C","D"):
        flags.append("cost_vs_experience")
    return flags

def confidence_label(answers, flags):
    if len(answers) < 40:
        return "Low"
    if len(flags) == 0:
        return "High"
    if len(flags) == 1:
        return "Medium"
    return "Low"

def top_dimensions(scores):
    items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    max_score = max(1, items[0][1])
    out = []
    for k,v in items:
        pct = int(max(0, min(100, round((v / max_score) * 100))))
        out.append({"code": k, "label": LABELS[k], "value": pct, "raw": v})
    return out

def primary_archetype(scores):
    ordered = [k for k,_ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
    top = ordered[:4]
    val, perf, emo, sta, con, pln, reg, inf, exp = [scores[d] for d in DIMENSIONS]
    if inf + emo + exp > val + perf + pln and inf > 0.75 * max(1, max(scores.values())):
        return "FOMO-Driven Upgrader"
    if val >= perf and val >= emo and con >= max(emo, sta) and val >= inf:
        return "Value Optimizer"
    if perf >= val and perf >= emo and perf >= sta:
        return "Performance Seeker"
    if emo >= max(val, perf) and emo >= sta and emo >= inf:
        return "Emotional Spender"
    if sta >= max(val, perf) and sta >= emo:
        return "Identity Curator"
    if con >= max(val, perf, emo) and con >= sta:
        return "Convenience Maximizer"
    if reg >= max(val, perf, emo) and pln >= emo:
        return "Regret Avoider"
    if inf >= max(val, perf, emo):
        return "Socially Influenced Buyer"
    if exp >= max(val, perf, emo) and emo >= val:
        return "Experience Chaser"
    if val >= 0.9*perf and reg > 0 and pln > 0:
        return "Over-Optimizer"
    if emo > 0 and pln < 0:
        return "Impulse Reactor"
    return "Balanced Strategist"

def build_report(scores, answers):
    dims = top_dimensions(scores)
    primary = primary_archetype(scores)
    meta = ARCHETYPES[primary]

    top_labels = [LABELS[d["code"]].lower() for d in dims[:3]]

    page_1 = f"""
You are not careless with decisions.

You think more than most people realize.

There is a pattern in how you approach choices. You don’t jump. You evaluate. You compare. You try to make sure that what you choose will hold up over time.

At your best, this makes you someone who avoids mistakes others regret.

But there is another side to this.

There are moments where the decision is already clear… and yet something in you keeps going.

Not because you are lost.

But because you want to be sure.
"""

    page_2 = f"""
Your decisions tend to be driven by {top_labels[0]}, reinforced by {top_labels[1]}.

This means you are not reacting randomly to what is in front of you.

You are filtering everything through an internal system:
- Does this make sense?
- Will this hold up?
- Is this the right move long term?

That internal system is strong.

But it also means decisions can become heavier than they need to be.
"""

    page_3 = """
There is a hidden cost to this pattern.

Not in money.

In energy.

You can spend more time than necessary comparing, validating, and re-checking decisions that are already good enough.

And over time, that creates something subtle:

Decision fatigue.

And sometimes… missed timing.
"""

    page_4 = """
This pattern does not stay only in spending.

It can show up in:
- how long you take to make important life decisions
- how often you revisit choices after they are already made
- how much pressure you place on yourself to “get it right”

In relationships, this can look like overthinking.
In work, it can look like hesitation before acting.

Not because you are unsure.

But because you care about making the right move.
"""

    page_5 = """
Your strengths are real:

- You do not act blindly
- You think before committing
- You value clarity and structure
- You avoid unnecessary mistakes

When this is balanced, it becomes a powerful advantage.

You make solid decisions.
"""

    page_6 = """
What to watch:

- Over-comparing beyond what is useful
- Searching for certainty when enough information is already present
- Delaying action in situations that require movement

The risk is not making a bad decision.

The risk is taking too long to make a good one.
"""

    page_7 = """
As your life evolves, this pattern may shift.

With more resources, you may start valuing time over optimization.

With more pressure, you may feel the weight of decisions more strongly.

The pattern does not disappear.

It adapts.
"""

    page_8 = """
What to do differently:

- Define what “good enough” means before comparing options
- Set time limits for decisions that do not require perfection
- Recognize when continued analysis is no longer adding value

Closing insight:

You do not need perfect decisions.

You need timely ones.
"""

    return {
        "page_1": page_1,
        "page_2": page_2,
        "page_3": page_3,
        "page_4": page_4,
        "page_5": page_5,
        "page_6": page_6,
        "page_7": page_7,
        "page_8": page_8,
        "primary": primary,
        "confidence": "High confidence"
    }
def setup():
    init_db()
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    if "answers" not in session:
        session["answers"] = {}
    if "creator" not in session:
        session["creator"] = request.args.get("creator", "")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/test", methods=["GET","POST"])
def test():
    answers = session.get("answers", {})
    current = len(answers) + 1
    if request.method == "POST":
        ans = request.form.get("answer")
        if ans in ("A","B","C","D"):
            answers[str(current)] = ans
            session["answers"] = answers
            current += 1
    if current > 40:
        return redirect(url_for("analyze"))
    q = QUESTIONS[current-1]
    return render_template("question.html", q=q)

@app.route("/analyze")
def analyze():
    return render_template("analyze.html")

@app.route("/result")
def result():
    answers = session.get("answers", {})
    if len(answers) < 40:
        return redirect(url_for("test"))
    report = build_report(compute_scores(answers), answers)
    session["report"] = report
    return render_template("result.html", **report)

@app.route("/details", methods=["GET","POST"])
def details():
    data = session.get("details", {})
    if request.method == "POST":
        data = {
            "name": request.form.get("name","").strip(),
            "social_platform": request.form.get("social_platform","").strip(),
            "social_handle": request.form.get("social_handle","").strip(),
            "gender": request.form.get("gender","").strip(),
            "age_range": request.form.get("age_range","").strip(),
            "email": request.form.get("email","").strip(),
        }
        session["details"] = data
        save_current_record()
        return render_template("thanks.html")
    return render_template("details.html", data=data)

@app.route("/full-report")
def full_report():
    answers = session.get("answers", {})
    if len(answers) < 40:
        return redirect(url_for("test"))
    report = session.get("report") or build_report(compute_scores(answers), answers)
    return render_template("report.html", **report)

def save_current_record():
    answers = session.get("answers", {})
    report = session.get("report") or build_report(compute_scores(answers), answers)
    details = session.get("details", {})
    conn = get_db()
    conn.execute(
        "INSERT INTO responses (session_id, creator, answers_json, result_json, name, social_platform, social_handle, gender, age_range, email, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            session.get("session_id"),
            session.get("creator",""),
            json.dumps(answers),
            json.dumps(report),
            details.get("name",""),
            details.get("social_platform",""),
            details.get("social_handle",""),
            details.get("gender",""),
            details.get("age_range",""),
            details.get("email",""),
            datetime.utcnow().isoformat()
        )
    )
    conn.commit()
    conn.close()

@app.route("/admin/export.csv")
def export_csv():
    conn = get_db()
    rows = conn.execute("SELECT * FROM responses ORDER BY id DESC").fetchall()
    import csv, tempfile
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id","session_id","creator","name","social_platform","social_handle","gender","age_range","email","created_at","answers_json","result_json"])
        for r in rows:
            writer.writerow([r["id"], r["session_id"], r["creator"], r["name"], r["social_platform"], r["social_handle"], r["gender"], r["age_range"], r["email"], r["created_at"], r["answers_json"], r["result_json"]])
    return send_file(path, as_attachment=True, download_name="bsa_export.csv")

@app.route("/export-me")
def export_me():
    answers = session.get("answers", {})
    report = session.get("report") or build_report(compute_scores(answers), answers)
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "creator": session.get("creator",""),
            "answers": answers,
            "details": session.get("details", {}),
            "report": report
        }, f, indent=2)
    return send_file(path, as_attachment=True, download_name="bsa_profile.json")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
