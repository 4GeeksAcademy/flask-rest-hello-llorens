from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

    
class People(db.Model):
    Id = db.Column(db.Integer, primary_key = True)
    Name = db.Column(db.String(50), nullable = False)
    Last_Name = db.Column(db.String(50), nullable = False)
    Age = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f'<Name {self.Name}>'

class Planets(db.Model):
    Id = db.Column(db.Integer, primary_key = True)
    Name = db.Column(db.String(50), nullable = False)
    Population = db.Column(db.Integer, nullable = False)
    Width = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f'<Name {self.Name}>'