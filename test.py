from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=365)
db = SQLAlchemy(app)

class Vent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    same = db.Column(db.Integer, default=0)
    support = db.Column(db.Integer, default=0)
    love = db.Column(db.Integer, default=0)

class UserReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    vent_id = db.Column(db.Integer, nullable=False)
    reaction = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    return render_template('vent.html')

@app.route('/vent', methods=['GET', 'POST'])
def vent():
    if request.method == 'POST':
        vent_content = request.form['message']
        new_vent = Vent(content=vent_content)
        db.session.add(new_vent)
        db.session.commit()
        return render_template('vent_submitted.html', vent_id=new_vent.id)
    else:
        return render_template('vent.html')

@app.route('/view')
def view():
    initial_vent = Vent.query.order_by(db.func.random()).first()
    return render_template('view.html', initial_vent=initial_vent)

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/update_counter/<int:id>/<interaction>', methods=['POST'])
def update_counter(id, interaction):
    session_id = session.sid if hasattr(session, 'sid') else str(random.randint(100000, 999999))
    session['sid'] = session_id
    existing_reaction = UserReaction.query.filter_by(session_id=session_id, vent_id=id, reaction=interaction).first()

    vent = Vent.query.get(id)
    if not vent:
        return jsonify({'success': False, 'message': 'Vent not found.'})

    if existing_reaction:
        # Unreact
        if interaction == 'same':
            vent.same = (vent.same or 1) - 1
        elif interaction == 'support':
            vent.support = (vent.support or 1) - 1
        elif interaction == 'love':
            vent.love = (vent.love or 1) - 1
        db.session.delete(existing_reaction)
    else:
        # React
        if interaction == 'same':
            vent.same = (vent.same or 0) + 1
        elif interaction == 'support':
            vent.support = (vent.support or 0) + 1
        elif interaction == 'love':
            vent.love = (vent.love or 0) + 1
        new_reaction = UserReaction(session_id=session_id, vent_id=id, reaction=interaction)
        db.session.add(new_reaction)

    db.session.commit()
    
    return jsonify({'success': True, 'same': vent.same, 'support': vent.support, 'love': vent.love})

@app.route('/get_vent/<int:id>/<direction>')
def get_vent(id, direction):
    if direction == 'next':
        vent = Vent.query.filter(Vent.id > id).order_by(Vent.id.asc()).first()
    elif direction == 'prev':
        vent = Vent.query.filter(Vent.id < id).order_by(Vent.id.desc()).first()

    if vent:
        return jsonify({'id': vent.id, 'content': vent.content, 'same': vent.same, 'support': vent.support, 'love': vent.love})
    else:
        return jsonify({'id': None, 'content': 'No more vents available.', 'same': 0, 'support': 0, 'love': 0})

@app.route('/get_vent_by_id/<int:id>')
def get_vent_by_id(id):
    vent = Vent.query.get(id)
    if vent:
        return jsonify({'id': vent.id, 'content': vent.content, 'same': vent.same, 'support': vent.support, 'love': vent.love})
    else:
        return jsonify({'id': None, 'content': 'Vent not found.', 'same': 0, 'support': 0, 'love': 0})

if __name__ == '__main__':
    app.run(debug=True)
