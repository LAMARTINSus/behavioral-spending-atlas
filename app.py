import json, os, sqlite3, uuid
from datetime import datetime
from flask import Flask, g, redirect, render_template, request, session, url_for, send_file, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-me')
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'bsa_sample.db')

DIMENSIONS = ['SEC','EXP','STA','VAL','INF','CON','PLN','EMO','REG']

QUESTIONS = [
    {
        'id':'Q01','section':'Your Internal Compass',
        'question':'When life feels uncertain, what restores your sense of balance fastest?',
        'options':{
            'A':'Knowing things are secured',
            'B':'Having multiple options open',
            'C':'Enjoying something in the present',
            'D':'Organizing things efficiently'
        }
    },
    {'id':'Q02','section':'Your Internal Compass','question':'When something costs more but feels “right,” what is that feeling tied to?','options':{'A':'Longevity','B':'Alignment with self','C':'Perception or elevation','D':'Practical usefulness'}},
    {'id':'Q03','section':'Your Internal Compass','question':'Which tension is hardest to carry?','options':{'A':'Losing money unnecessarily','B':'Letting an experience pass','C':'Being perceived incorrectly','D':'Choosing imperfectly'}},
    {'id':'Q04','section':'Your Internal Compass','question':'When you picture a person thriving, what defines it most?','options':{'A':'Stability','B':'Freedom of choice','C':'Visible lifestyle','D':'Control over life systems'}},
    {'id':'Q05','section':'Your Internal Compass','question':'Without overthinking, money feels most like:','options':{'A':'Protection','B':'Possibility','C':'Expression','D':'Structure'}},
    {'id':'Q06','section':'Your Internal Compass','question':'After a meaningful purchase, what shows up first?','options':{'A':'Grounding','B':'Energy','C':'Awareness of cost','D':'Reflection on decision'}},
    {'id':'Q07','section':'Your Internal Compass','question':'Which approach feels most natural over time?','options':{'A':'Anticipate and prepare','B':'Stay adaptable','C':'Act when it feels right','D':'Reduce inefficiencies'}},
    {'id':'Q08','section':'Your Internal Compass','question':'Others would most likely describe your relationship with spending as:','options':{'A':'Careful','B':'Open','C':'Enjoying','D':'Calculated'}},
    {'id':'Q09','section':'Your Internal Compass','question':'When quality and price are both high, your internal response is:','options':{'A':'I can justify this','B':'I pause','C':'I feel drawn to it','D':'I dissect it'}},
    {'id':'Q10','section':'Your Internal Compass','question':'Looking ahead financially, what matters most?','options':{'A':'Safety','B':'Flexibility','C':'Life experiences','D':'Optimization'}},
    {'id':'Q11','section':'Your Internal Compass','question':'Which thought pattern appears more often?','options':{'A':'Protect what I have','B':'Use what I have','C':'Enhance what I have','D':'Improve how I use it'}},
    {'id':'Q12','section':'Your Internal Compass','question':'Which outcome feels most rewarding?','options':{'A':'Preserving resources','B':'Creating experiences','C':'Elevating quality','D':'Maximizing efficiency'}},
    {'id':'Q13','section':'Your External Field','question':'A trusted person recommends something beyond your usual range. Your first instinct:','options':{'A':'Lean into their trust','B':'Validate independently','C':'Let it sit','D':'Disconnect from it'}},
    {'id':'Q14','section':'Your External Field','question':'When something is widely respected, your reaction is:','options':{'A':'It gains credibility','B':'It earns consideration','C':'It changes little','D':'It raises skepticism'}},
    {'id':'Q15','section':'Your External Field','question':'When people similar to you endorse something:','options':{'A':'It strongly influences you','B':'It helps guide','C':'It is just information','D':'It is irrelevant'}},
    {'id':'Q16','section':'Your External Field','question':'Before trying something new, what anchors you most?','options':{'A':'Familiar voices','B':'Data or feedback','C':'Internal sense','D':'External reputation'}},
    {'id':'Q17','section':'Your External Field','question':'When something gains rapid popularity:','options':{'A':'You move toward it','B':'You analyze it','C':'You ignore it','D':'You question it'}},
    {'id':'Q18','section':'Your External Field','question':'If something signals prestige, you:','options':{'A':'Notice immediately','B':'Factor it in','C':'Neutralize it','D':'Reject it'}},
    {'id':'Q19','section':'Your External Field','question':'When someone you admire chooses something:','options':{'A':'You lean toward it','B':'You evaluate it','C':'You stay independent','D':'You detach from it'}},
    {'id':'Q20','section':'Your External Field','question':'In a group decision above your comfort level:','options':{'A':'You align','B':'You negotiate','C':'You withdraw quietly','D':'You step out'}},
    {'id':'Q21','section':'Your External Field','question':'When access is limited or exclusive:','options':{'A':'It attracts you','B':'It interests you','C':'It raises questions','D':'It reduces interest'}},
    {'id':'Q22','section':'Your External Field','question':'Which carries more weight in decisions?','options':{'A':'Social perception','B':'Logical reasoning','C':'Internal alignment','D':'Functional outcome'}},
    {'id':'Q23','section':'Your External Field','question':'When others enjoy something visibly:','options':{'A':'You want to experience it','B':'You become curious','C':'You observe','D':'You disengage'}},
    {'id':'Q24','section':'Your External Field','question':'Which best reflects your influence style?','options':{'A':'Absorbing','B':'Filtering','C':'Independent','D':'Resistant'}},
    {'id':'Q25','section':'Your Decision System','question':'An unexpected financial gain appears. You:','options':{'A':'Preserve it','B':'Divide it','C':'Use it','D':'Upgrade something'}},
    {'id':'Q26','section':'Your Decision System','question':'Faced with time vs money:','options':{'A':'Time wins','B':'It depends','C':'Money wins','D':'Efficiency wins'}},
    {'id':'Q27','section':'Your Decision System','question':'A small enhancement appears at checkout:','options':{'A':'Add it','B':'Consider it','C':'Decline it','D':'Only if necessary'}},
    {'id':'Q28','section':'Your Decision System','question':'Between effort and ease:','options':{'A':'Prefer ease','B':'Balance','C':'Accept effort','D':'Optimize path'}},
    {'id':'Q29','section':'Your Decision System','question':'Which after-effect lingers longer?','options':{'A':'Spending too much','B':'Missing something','C':'Poor usefulness','D':'Over-analysis'}},
    {'id':'Q30','section':'Your Decision System','question':'When comparing options:','options':{'A':'You enjoy it','B':'You tolerate it','C':'You avoid it','D':'You shortcut it'}},
    {'id':'Q31','section':'Your Decision System','question':'When something depletes:','options':{'A':'Replace quickly','B':'Re-evaluate','C':'Delay','D':'Improve version'}},
    {'id':'Q32','section':'Your Decision System','question':'Decision speed is typically:','options':{'A':'Immediate','B':'Moderate','C':'Deliberate','D':'Context-based'}},
    {'id':'Q33','section':'Your Decision System','question':'A slightly better but costlier option appears:','options':{'A':'Upgrade','B':'Consider','C':'Stay','D':'Analyze deeply'}},
    {'id':'Q34','section':'Your Decision System','question':'Finding a better option after buying:','options':{'A':'Frustrates you','B':'Doesn’t affect much','C':'You accept it','D':'You adapt learning'}},
    {'id':'Q35','section':'Your Decision System','question':'Planning purchases:','options':{'A':'Consistent','B':'Frequent','C':'Minimal','D':'Situational'}},
    {'id':'Q36','section':'Your Decision System','question':'Your natural spending rhythm:','options':{'A':'Controlled','B':'Balanced','C':'Enjoyable','D':'Refined'}},
]

SCORING = {
'Q01': {'A': {'SEC':2,'PLN':1}, 'B': {'EXP':2}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q02': {'A': {'SEC':2}, 'B': {'EMO':2}, 'C': {'STA':2}, 'D': {'VAL':2}},
'Q03': {'A': {'REG':2}, 'B': {'EXP':2}, 'C': {'STA':2}, 'D': {'VAL':2}},
'Q04': {'A': {'SEC':2}, 'B': {'EXP':2}, 'C': {'STA':2}, 'D': {'PLN':2}},
'Q05': {'A': {'SEC':2}, 'B': {'EXP':2}, 'C': {'STA':2}, 'D': {'PLN':2}},
'Q06': {'A': {'SEC':2}, 'B': {'EMO':2}, 'C': {'REG':2}, 'D': {'VAL':2}},
'Q07': {'A': {'PLN':2}, 'B': {'EXP':2}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q08': {'A': {'SEC':2}, 'B': {'EXP':2}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q09': {'A': {'STA':2}, 'B': {'REG':2}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q10': {'A': {'SEC':2}, 'B': {'EXP':2}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q11': {'A': {'SEC':2}, 'B': {'EXP':2}, 'C': {'STA':2}, 'D': {'VAL':2}},
'Q12': {'A': {'SEC':2}, 'B': {'EXP':2}, 'C': {'STA':2}, 'D': {'VAL':2}},
'Q13': {'A': {'INF':2}, 'B': {'VAL':2}, 'C': {'REG':1}, 'D': {'PLN':2}},
'Q14': {'A': {'INF':2}, 'B': {'INF':1}, 'C': {'PLN':2}, 'D': {'VAL':2}},
'Q15': {'A': {'INF':2}, 'B': {'INF':1}, 'C': {'PLN':2}, 'D': {'VAL':2}},
'Q16': {'A': {'INF':2}, 'B': {'VAL':2}, 'C': {'PLN':2}, 'D': {'STA':2}},
'Q17': {'A': {'INF':2}, 'B': {'VAL':2}, 'C': {'PLN':2}, 'D': {'VAL':2,'REG':1}},
'Q18': {'A': {'STA':2}, 'B': {'STA':1}, 'C': {'PLN':2}, 'D': {'VAL':2}},
'Q19': {'A': {'INF':2}, 'B': {'VAL':2}, 'C': {'PLN':2}, 'D': {'REG':2}},
'Q20': {'A': {'INF':2}, 'B': {'VAL':2}, 'C': {'REG':1}, 'D': {'PLN':2}},
'Q21': {'A': {'STA':2}, 'B': {'STA':1}, 'C': {'VAL':2}, 'D': {'PLN':2}},
'Q22': {'A': {'INF':2}, 'B': {'VAL':2}, 'C': {'EMO':2}, 'D': {'PLN':2}},
'Q23': {'A': {'INF':2}, 'B': {'INF':1}, 'C': {'PLN':2}, 'D': {'REG':2}},
'Q24': {'A': {'INF':2}, 'B': {'INF':1}, 'C': {'PLN':2}, 'D': {'REG':2}},
'Q25': {'A': {'SEC':2}, 'B': {'VAL':2}, 'C': {'EMO':2}, 'D': {'STA':2}},
'Q26': {'A': {'CON':2}, 'B': {'CON':1}, 'C': {'VAL':2}, 'D': {'PLN':2}},
'Q27': {'A': {'EMO':2}, 'B': {'EMO':1}, 'C': {'SEC':2}, 'D': {'VAL':2}},
'Q28': {'A': {'CON':2}, 'B': {'CON':1}, 'C': {'VAL':2}, 'D': {'PLN':2}},
'Q29': {'A': {'REG':2}, 'B': {'EXP':2}, 'C': {'VAL':2}, 'D': {'PLN':2}},
'Q30': {'A': {'VAL':2}, 'B': {'VAL':1}, 'C': {'CON':2}, 'D': {'PLN':2}},
'Q31': {'A': {'CON':2}, 'B': {'VAL':2}, 'C': {'SEC':2}, 'D': {'STA':2}},
'Q32': {'A': {'EMO':2}, 'B': {'EMO':1}, 'C': {'PLN':2}, 'D': {'VAL':2}},
'Q33': {'A': {'STA':2}, 'B': {'STA':1}, 'C': {'SEC':2}, 'D': {'VAL':2}},
'Q34': {'A': {'REG':2}, 'B': {'REG':1}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q35': {'A': {'PLN':2}, 'B': {'PLN':1}, 'C': {'EMO':2}, 'D': {'VAL':2}},
'Q36': {'A': {'SEC':2}, 'B': {'VAL':2}, 'C': {'EMO':2}, 'D': {'PLN':2}},
}

ARCHETYPES = {
    'Protective Planner': {'core':['SEC','PLN','REG'], 'summary':'You are guided by protection, stability, and thoughtful control. You naturally filter spending through safety and future consequences.', 'strengths':['Disciplined with money','Thinks ahead','Low impulse spending'], 'blind_spots':['Can over-restrict enjoyment','May delay good decisions too long','Can treat uncertainty like danger']},
    'Quiet Optimizer': {'core':['VAL','PLN','REG'], 'summary':'You like decisions that make sense. You prefer intelligent spending, clean logic, and strong value over flash or emotional momentum.', 'strengths':['Strong decision logic','Good at extracting value','Low waste orientation'], 'blind_spots':['Can over-analyze','May undervalue emotion or delight','Can lose time chasing the perfect choice']},
    'Selective Indulger': {'core':['EXP','EMO','VAL'], 'summary':'You enjoy life, but you usually want a reason. You tend to spend when enjoyment feels meaningful, justified, or aligned with the moment.', 'strengths':['Balances pleasure and reason','Can enjoy money consciously','Often self-aware'], 'blind_spots':['Can justify emotional spending','Convenience can hide impulse','Experience can override budget']},
    'Status-Calibrated Buyer': {'core':['STA','INF','EXP'], 'summary':'You are sensitive to quality, image, and what choices represent. Your spending often reflects standards, positioning, and visible elevation.', 'strengths':['High standards','Appreciates refinement','Strong sense of identity in choices'], 'blind_spots':['Can overpay for perception','Prestige cues can sway you','Social context may shift decisions']},
    'Socially Guided Explorer': {'core':['INF','EXP','STA'], 'summary':'You are open to discovery and often moved by trusted people, visible enjoyment, and shared momentum. Influence travels through your relationships.', 'strengths':['Open-minded','Adaptive','Learns through community'], 'blind_spots':['Can be vulnerable to FOMO','Recommendations can bypass your filter','Social proof may feel like truth']},
    'Comfort-Driven Spender': {'core':['EMO','CON','EXP'], 'summary':'You are drawn to what feels good, easy, and relieving. Spending can become a tool for comfort, reward, or emotional softening.', 'strengths':['Knows what feels nourishing','Enjoys life in the moment','Can create comfort quickly'], 'blind_spots':['Stress can trigger purchases','Convenience premiums add up','Mood can drive spending more than logic']},
    'Friction-Avoidant Consumer': {'core':['CON','EMO','VAL'], 'summary':'You strongly prefer smoothness and ease. When something reduces effort, saves energy, or simplifies life, it becomes much more attractive.', 'strengths':['Fast decisions','Protects energy','Values practical ease'], 'blind_spots':['May overpay for convenience','Can skip deeper comparison','Subscriptions and small add-ons can accumulate']},
    'Value Hunter': {'core':['VAL','SEC','REG'], 'summary':'You want strong returns from every dollar. You dislike waste, notice price-value mismatches quickly, and prefer to feel smart after spending.', 'strengths':['Sharp value detection','Resourceful','Protective against waste'], 'blind_spots':['Can focus too much on price','Cheap can masquerade as smart','May miss higher-value premium options']},
    'Aspirational Upgrader': {'core':['STA','EXP','EMO'], 'summary':'You are motivated by progress, better experiences, and the next level. Your spending often expresses movement, growth, and improvement.', 'strengths':['Growth-oriented','Willing to invest in improvement','Strong aspiration energy'], 'blind_spots':['Can chase upgrades too often','May equate better with more expensive','Future-self fantasies can justify spending']},
    'Vigilant Preserver': {'core':['SEC','REG','PLN'], 'summary':'You are highly alert to loss, risk, and exposure. You preserve resources carefully and prefer choices that reduce downside.', 'strengths':['Careful steward','Risk-aware','Stable under financial uncertainty'], 'blind_spots':['Opportunity cost can be hidden','Caution can harden into fear','Can underinvest in quality of life']},
    'Emotionally Reactive Spender': {'core':['EMO','EXP','CON'], 'summary':'Your spending is sensitive to internal weather. Mood, pressure, reward, and relief can all shape choices more than you realize in the moment.', 'strengths':['Emotionally alive','Can find joy quickly','Sensitive to lived experience'], 'blind_spots':['Impulse cycles','Regret after relief spending','Hard to separate feeling from need']},
    'Identity Curator': {'core':['STA','EMO','VAL'], 'summary':'You use spending to align with who you are or who you believe you are becoming. Purchases can feel like personal statements.', 'strengths':['Intentional with meaning','Strong identity awareness','Values alignment'], 'blind_spots':['Can overpay for symbolic fit','Brand alignment can override practicality','Identity can become a spending trigger']}
}

MAX_BY_DIM = {d:0 for d in DIMENSIONS}
for qid, opts in SCORING.items():
    for dim in DIMENSIONS:
        MAX_BY_DIM[dim] += max((contrib.get(dim,0) for contrib in opts.values()), default=0)


def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        creator_id TEXT,
        started_at TEXT,
        completed_at TEXT,
        first_name TEXT,
        social_platform TEXT,
        social_handle TEXT,
        gender TEXT,
        age_range TEXT,
        email TEXT,
        primary_archetype TEXT,
        secondary_archetype TEXT,
        scores_json TEXT,
        normalized_json TEXT,
        preview_summary TEXT
    );
    CREATE TABLE IF NOT EXISTS responses (
        session_id TEXT,
        question_id TEXT,
        answer_key TEXT,
        PRIMARY KEY (session_id, question_id)
    );
    ''')
    db.commit()
    db.close()

# Initialize the SQLite database at startup so the app works on first boot in Render.
init_db()


def start_new_session(creator_id=None):
    sid = str(uuid.uuid4())
    db = get_db()
    db.execute('INSERT INTO sessions (id, creator_id, started_at) VALUES (?,?,?)',
               (sid, creator_id, datetime.utcnow().isoformat()))
    db.commit()
    session['bsa_session_id'] = sid
    session['creator_id'] = creator_id
    return sid


def current_session_id():
    sid = session.get('bsa_session_id')
    if not sid:
        sid = start_new_session(request.args.get('creator') or request.args.get('cid'))
    return sid


def compute_scores(answer_map):
    scores = {d:0 for d in DIMENSIONS}
    for q in QUESTIONS:
        qid = q['id']
        answer = answer_map.get(qid)
        if not answer:
            continue
        for dim, pts in SCORING[qid][answer].items():
            scores[dim] += pts
    normalized = {d: round(scores[d] / MAX_BY_DIM[d], 3) if MAX_BY_DIM[d] else 0 for d in DIMENSIONS}
    return scores, normalized


def similarity(normalized, core_dims):
    # simple average on core dims with slight bonus for balance
    vals = [normalized[d] for d in core_dims]
    return sum(vals)/len(vals)


def get_top_dims(normalized, n=3):
    return sorted(normalized.items(), key=lambda x: x[1], reverse=True)[:n]


def map_archetype(normalized):
    ranked = sorted(
        ((name, similarity(normalized, data['core'])) for name, data in ARCHETYPES.items()),
        key=lambda x: x[1], reverse=True
    )
    primary = ranked[0][0]
    secondary = ranked[1][0] if len(ranked) > 1 else None
    return primary, secondary


def build_result(primary, secondary, normalized, first_name=None):
    pdata = ARCHETYPES[primary]
    sdata = ARCHETYPES.get(secondary)
    top_dims = get_top_dims(normalized)
    top_dim_names = {
        'SEC':'security and stability',
        'EXP':'experience and freedom',
        'STA':'status and elevation',
        'VAL':'value and optimization',
        'INF':'social influence',
        'CON':'convenience and ease',
        'PLN':'planning and discipline',
        'EMO':'emotion and internal state',
        'REG':'regret sensitivity'
    }

    first_word = f"{first_name}, you" if first_name else 'You'
    headline = f"{primary} with a {secondary}" if secondary else primary
    overview = (
        f"{first_word} tend to make money decisions through the lens of {pdata['summary'].lower()} "
        f"Your strongest pattern is shaped by {', '.join(top_dim_names[d] for d, _ in top_dims[:2])}."
    )

    strengths = list(pdata['strengths'])
    blind_spots = list(pdata['blind_spots'])
    deep = []
    behavior_notes = []
    next_moves = []

    if normalized['EMO'] > 0.65 and normalized['CON'] > 0.55:
        deep.append('When emotion and ease align, you may spend faster than you realize.')
        behavior_notes.append('Fast, low-friction purchases can feel harmless in the moment but become expensive in aggregate.')
        next_moves.append('Create a pause rule for emotional or convenience-based purchases.')
    if normalized['INF'] > 0.6 and normalized['STA'] > 0.5:
        deep.append('Prestige and social proof can quietly increase the pull of certain offers.')
        behavior_notes.append('The people, signals, and status around a purchase may affect you more than the product itself.')
        next_moves.append('Ask whether you want the item itself or the feeling it represents.')
    if normalized['VAL'] > 0.65 and normalized['REG'] > 0.5:
        deep.append('You dislike waste and may revisit decisions mentally after a purchase.')
        behavior_notes.append('You often seek reassurance that money was spent wisely, which can lead to over-comparison.')
        next_moves.append('Set a “good enough” threshold before comparing too many options.')
    if normalized['SEC'] > 0.65 and normalized['PLN'] > 0.6:
        deep.append('You tend to make your best decisions when you can prepare before the moment of purchase.')
        behavior_notes.append('Preparation lowers stress and makes your financial judgment much stronger.')
        next_moves.append('Pre-decide spending ranges before emotionally charged situations.')
    if normalized['EXP'] > 0.6 and normalized['EMO'] > 0.55:
        behavior_notes.append('You are most alive when money creates memorable experiences, not just possessions.')
        next_moves.append('Protect a specific budget for meaningful experiences so enjoyment stays intentional.')
    if normalized['STA'] > 0.6 and normalized['VAL'] > 0.5:
        behavior_notes.append('You are attracted to things that feel elevated, but you still want a strong rationale behind the upgrade.')
        next_moves.append('Separate true quality from image-based premiums before upgrading.')
    if normalized['SEC'] > 0.6 and normalized['REG'] > 0.55:
        behavior_notes.append('Loss prevention is a strong internal driver, which helps discipline but can hide opportunity cost.')
        next_moves.append('Define a safe zone for spending that improves life without feeling irresponsible.')
    if normalized['INF'] < 0.35:
        behavior_notes.append('You are not easily moved by other people’s preferences, which protects you from hype.')
    if normalized['PLN'] < 0.35 and normalized['EMO'] > 0.55:
        blind_spots.append('Low planning combined with emotional momentum can create “why did I buy that?” moments.')

    if not deep:
        deep.append('Your strongest decisions happen when your top drivers are aligned instead of competing with each other.')
    if not behavior_notes:
        behavior_notes.append('Your pattern is relatively balanced, which means context often determines whether you spend with clarity or drift.')
    if not next_moves:
        next_moves.append('Make your next few purchases more conscious by naming the real reason behind them before you buy.')

    dimension_story = [
        {
            'code': dim,
            'label': top_dim_names[dim].title(),
            'value': score,
            'percent': round(score * 100)
        } for dim, score in top_dims
    ]

    return {
        'headline': headline,
        'overview': overview,
        'strengths': strengths,
        'blind_spots': blind_spots,
        'deep_insights': deep,
        'behavior_notes': behavior_notes,
        'next_moves': next_moves,
        'secondary_note': sdata['summary'] if sdata else None,
        'dimension_story': dimension_story,
        'identity_sentence': f"Your profile is anchored in {top_dim_names[top_dims[0][0]]}, reinforced by {top_dim_names[top_dims[1][0]]}.",
    }



@app.route('/')
def home():
    creator = request.args.get('creator') or request.args.get('cid')
    # reset session when a new creator link comes in
    if creator and session.get('creator_id') != creator:
        session.clear()
    current_session_id()
    return render_template('home.html')


@app.route('/start', methods=['POST'])
def start():
    current_session_id()
    return redirect(url_for('question', index=1))


@app.route('/question/<int:index>', methods=['GET', 'POST'])
def question(index):
    sid = current_session_id()
    if index < 1 or index > len(QUESTIONS):
        return redirect(url_for('result_preview'))
    q = QUESTIONS[index-1]
    db = get_db()
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer not in ['A','B','C','D']:
            return render_template('question.html', q=q, index=index, total=len(QUESTIONS), error='Please select one answer.')
        db.execute('INSERT OR REPLACE INTO responses (session_id, question_id, answer_key) VALUES (?,?,?)', (sid, q['id'], answer))
        db.commit()
        if index == len(QUESTIONS):
            return redirect(url_for('analyzing'))
        return redirect(url_for('question', index=index+1))
    existing = db.execute('SELECT answer_key FROM responses WHERE session_id=? AND question_id=?', (sid, q['id'])).fetchone()
    return render_template('question.html', q=q, index=index, total=len(QUESTIONS), selected=(existing['answer_key'] if existing else None))


@app.route('/analyzing')
def analyzing():
    sid = current_session_id()
    db = get_db()
    rows = db.execute('SELECT question_id, answer_key FROM responses WHERE session_id=?', (sid,)).fetchall()
    answer_map = {r['question_id']: r['answer_key'] for r in rows}
    if len(answer_map) < len(QUESTIONS):
        next_index = len(answer_map)+1
        return redirect(url_for('question', index=next_index))
    scores, normalized = compute_scores(answer_map)
    primary, secondary = map_archetype(normalized)
    result = build_result(primary, secondary, normalized)
    db.execute('UPDATE sessions SET completed_at=?, primary_archetype=?, secondary_archetype=?, scores_json=?, normalized_json=?, preview_summary=? WHERE id=?',
               (datetime.utcnow().isoformat(), primary, secondary, json.dumps(scores), json.dumps(normalized), result['overview'], sid))
    db.commit()
    return render_template('analyzing.html')


@app.route('/result')
def result_preview():
    sid = current_session_id()
    db = get_db()
    row = db.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
    if not row or not row['primary_archetype']:
        return redirect(url_for('question', index=1))
    normalized = json.loads(row['normalized_json'])
    result = build_result(row['primary_archetype'], row['secondary_archetype'], normalized, row['first_name'])
    return render_template('result.html', row=row, normalized=normalized, result=result)


@app.route('/profile/name', methods=['GET','POST'])
def profile_name():
    sid = current_session_id()
    db = get_db()
    if request.method == 'POST':
        first_name = request.form.get('first_name','').strip()
        db.execute('UPDATE sessions SET first_name=? WHERE id=?', (first_name, sid))
        db.commit()
        return redirect(url_for('profile_social'))
    row = db.execute('SELECT first_name FROM sessions WHERE id=?', (sid,)).fetchone()
    return render_template('profile_name.html', first_name=(row['first_name'] if row else ''))


@app.route('/profile/social', methods=['GET','POST'])
def profile_social():
    sid = current_session_id()
    db = get_db()
    if request.method == 'POST':
        platform = request.form.get('social_platform','')
        handle = request.form.get('social_handle','').strip()
        db.execute('UPDATE sessions SET social_platform=?, social_handle=? WHERE id=?', (platform, handle, sid))
        db.commit()
        return redirect(url_for('profile_demo'))
    row = db.execute('SELECT social_platform, social_handle FROM sessions WHERE id=?', (sid,)).fetchone()
    return render_template('profile_social.html', row=row)


@app.route('/profile/demo', methods=['GET','POST'])
def profile_demo():
    sid = current_session_id()
    db = get_db()
    if request.method == 'POST':
        gender = request.form.get('gender','')
        age_range = request.form.get('age_range','')
        db.execute('UPDATE sessions SET gender=?, age_range=? WHERE id=?', (gender, age_range, sid))
        db.commit()
        return redirect(url_for('profile_email'))
    row = db.execute('SELECT gender, age_range FROM sessions WHERE id=?', (sid,)).fetchone()
    return render_template('profile_demo.html', row=row)


@app.route('/profile/email', methods=['GET','POST'])
def profile_email():
    sid = current_session_id()
    db = get_db()
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        if not email:
            return render_template('profile_email.html', email='', error='Please enter your email to receive the report.')
        db.execute('UPDATE sessions SET email=? WHERE id=?', (email, sid))
        db.commit()
        return redirect(url_for('full_report'))
    row = db.execute('SELECT email FROM sessions WHERE id=?', (sid,)).fetchone()
    return render_template('profile_email.html', email=(row['email'] if row else ''))


@app.route('/report')
def full_report():
    sid = current_session_id()
    db = get_db()
    row = db.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
    if not row or not row['primary_archetype']:
        return redirect(url_for('home'))
    normalized = json.loads(row['normalized_json'])
    result = build_result(row['primary_archetype'], row['secondary_archetype'], normalized, row['first_name'])
    creator_name = row['creator_id'] or 'Direct'
    return render_template('report.html', row=row, normalized=normalized, result=result, creator_name=creator_name)


@app.route('/admin/export.csv')
def export_csv():
    db = get_db()
    rows = db.execute('SELECT * FROM sessions ORDER BY started_at DESC').fetchall()
    path = os.path.join(BASE_DIR, 'sample_export.csv')
    import csv
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id','creator_id','started_at','completed_at','first_name','social_platform','social_handle','gender','age_range','email','primary_archetype','secondary_archetype','preview_summary'])
        for r in rows:
            writer.writerow([r['id'], r['creator_id'], r['started_at'], r['completed_at'], r['first_name'], r['social_platform'], r['social_handle'], r['gender'], r['age_range'], r['email'], r['primary_archetype'], r['secondary_archetype'], r['preview_summary']])
    return send_file(path, as_attachment=True, download_name='bsa_sample_export.csv')


@app.route('/api/session')
def api_session():
    sid = current_session_id()
    db = get_db()
    row = db.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
    return jsonify({k: row[k] for k in row.keys()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
