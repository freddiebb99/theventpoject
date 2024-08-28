from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Vent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    same = db.Column(db.Integer)
    support = db.Column(db.Integer)
    love = db.Column(db.Integer)
    
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('vent.html')

# Vent Logic
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

# View Logic
@app.route('/view')
def view():
    vents = Vent.query.all()
    random_vent = random.choice(vents) if vents else None
    return render_template('view.html', initial_vent=random_vent)

@app.route('/update_counter/<int:id>/<interaction>', methods=['POST'])
def update_counter(id, interaction):
    vent = Vent.query.get(id)
    if not vent:
        return jsonify({'success': False, 'message': 'Vent not found.'})

    if interaction == 'same':
        vent.same = (vent.same or 0) + 1
    elif interaction == 'support':
        vent.support = (vent.support or 0) + 1
    elif interaction == 'love':
        vent.love = (vent.love or 0) + 1

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


# Events Page
@app.route('/events')
def events():
    return render_template('events.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
