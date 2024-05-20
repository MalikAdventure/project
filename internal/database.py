from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20))
    name = db.Column(db.String(20))


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    id_role = db.Column(db.Integer, db.ForeignKey('role.id'))
    full_name = db.Column(db.String(100))
    login = db.Column(db.String(100))
    password = db.Column(db.String(255))
    phone = db.Column(db.String(20))

    role = db.relationship('Role', backref='parent', lazy=True)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20))
    name = db.Column(db.String(20))


class Request(db.Model):
    __tablename__ = 'request'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    auto = db.Column(db.String(255))
    problem = db.Column(db.Text)
    id_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    booking_datetime = db.Column(db.DateTime)

    user = db.relationship('User', backref='parent', lazy=True)
    status = db.relationship('Status', backref='parent', lazy=True)
