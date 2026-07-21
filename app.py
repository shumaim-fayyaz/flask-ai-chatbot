from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from decouple import config
from models import db, User, ChatSession, Message
import cohere
import markdown
from markupsafe import Markup
from datetime import datetime


app = Flask(__name__)

# Add this custom filter right after defining 'app'
@app.template_filter('markdown')
def render_markdown(text):
    # fenced_code handles code blocks, nl2br handles line breaks properly
    return Markup(markdown.markdown(text, extensions=['fenced_code', 'nl2br']))

# Configuration
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL', default='sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Redirecting to the 'chat' route (which we will build next)
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- WE WILL INJECT THE CHAT, SEARCH, AND API ROUTES HERE ---

# Create the database tables before the first request
with app.app_context():
    db.create_all()



# Initialize Cohere Client
co = cohere.Client(config('COHERE_API_KEY'))
MASTER_PROMPT = """You are a highly capable, general-purpose AI assistant. 
You provide clear, concise, and accurate answers to all types of questions. 
Maintain a helpful and professional tone."""

@app.route('/', methods=['GET', 'POST'])
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # Fetch the trial count from the cookie, default to 0
    trial_count = int(request.cookies.get('trial_count', 0))
    chat_history = []
    
    if request.method == 'POST':
        user_input = request.form.get('prompt')
        if not user_input:
            return redirect(url_for('chat'))

        # --- ANONYMOUS USER (TRIAL LOGIC) ---
        if not current_user.is_authenticated:
            if trial_count >= 5:
                flash('Trial limit reached. Please register or log in to continue.', 'warning')
                return redirect(url_for('register'))
            
            # Call API without history and without saving to DB
            response = co.chat(
                message=user_input,
                model="command-a-03-2025",
                preamble=MASTER_PROMPT
            )
            
            # Create a response object so we can set the incremented cookie
            resp = make_response(render_template(
                'chat.html', 
                trial_response=response.text, 
                trial_prompt=user_input,
                trial_count=trial_count + 1
            ))
            # Set cookie to expire in 30 days
            resp.set_cookie('trial_count', str(trial_count + 1), max_age=60*60*24*30)
            return resp

        # --- LOGGED IN USER (DATABASE LOGIC) ---
        else:
            # Grab their latest chat session or create a new one
            session = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.date_created.desc()).first()
            if not session:
                session = ChatSession(title=f"Chat {datetime.utcnow().strftime('%Y-%m-%d')}", user_id=current_user.id)
                db.session.add(session)
                db.session.commit()
            
            # 1. Save user prompt to DB
            user_msg = Message(role='USER', content=user_input, session_id=session.id)
            db.session.add(user_msg)
            db.session.commit()
            
            # 2. Reconstruct history for Cohere context
            db_messages = Message.query.filter_by(session_id=session.id).order_by(Message.timestamp.asc()).all()
            # Cohere expects everything BEFORE the current prompt as chat_history
            cohere_history = [{"role": m.role, "message": m.content} for m in db_messages[:-1]]
            
            # 3. Hit the API
            response = co.chat(
                message=user_input,
                model="command-a-03-2025",
                preamble=MASTER_PROMPT,
                chat_history=cohere_history
            )
            
            # 4. Save AI response to DB
            ai_msg = Message(role='CHATBOT', content=response.text, session_id=session.id)
            db.session.add(ai_msg)
            db.session.commit()
            
            return redirect(url_for('chat'))

    # --- GET REQUEST (LOADING THE PAGE) ---
    if current_user.is_authenticated:
        session = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.date_created.desc()).first()
        if session:
            chat_history = Message.query.filter_by(session_id=session.id).order_by(Message.timestamp.asc()).all()
            
    return render_template('chat.html', chat_history=chat_history, trial_count=trial_count)


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q')
    results = []
    
    if query:
        # Cross-reference Messages with ChatSessions owned by the current user
        results = Message.query.join(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            Message.content.ilike(f'%{query}%')
        ).order_by(Message.timestamp.desc()).all()
        
    return render_template('search.html', results=results, search_query=query)
















if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    
    

    