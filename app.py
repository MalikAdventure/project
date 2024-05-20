from flask import *
from internal.database import *
from flask_bcrypt import Bcrypt
from flask_login import *
import config
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
app.config['SECRET_KEY'] = config.SECRET_KEY

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

with app.app_context():
    db.create_all()

    if not Role.query.filter_by(code='user').first():
        role_user = Role(code='user', name='Зарегистрированный пользователь')
        db.session.add(role_user)

    if not Role.query.filter_by(code='admin').first():
        role_admin = Role(code='admin', name='Администратор')
        db.session.add(role_admin)

    if not Status.query.filter_by(code='new').first():
        status_new = Status(code='new', name='Новое')
        db.session.add(status_new)
    
    if not Status.query.filter_by(code='canceled').first():
        status_canceled = Status(code='canceled', name='Отменено')
        db.session.add(status_canceled)
    
    if not Status.query.filter_by(code='confirmed').first():
        status_confirmed = Status(code='confirmed', name='Подтверждено')
        db.session.add(status_confirmed)

    if not User.query.filter_by(login='newfit').first():
        admin = User(
            login='newfit',
            phone='+18625128121',
            full_name='main admin',
            password=bcrypt.generate_password_hash('qsw123').decode('utf-8'),
            id_role=2,
        )
        db.session.add(admin)
    
    db.session.commit()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = dict(request.form)
        
        user = User.query.filter_by(login=data.get("login")).first()
        if not user:
            flash("Неверный логин или пароль", category='red')
        elif not bcrypt.check_password_hash(user.password, data.get("password")):
            flash("Неверный логин или пароль", category='red')
        else:
            login_user(user, remember=True)
            return redirect(url_for('index'))
    
    return render_template('login.html')



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = dict(request.form)

        error = False

        user = User.query.filter_by(login=data.get("login")).first()

        if user:
            flash('Пользователь с такой почтой уже существует', category='red')
            error = True
        
        if data.get('password') != data.get('re_password'):
            flash('Пароли не совпадают', category='red')
            error = True
        
        if not error:
            hash = bcrypt.generate_password_hash(data.pop('password')).decode('utf-8')
            
            data.pop('re_password')

            user = User(password=hash, id_role=1, **data)
            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)

            flash('Вы успешно зарегистировались', category='green')

            return redirect(url_for('index'))

    return render_template('register.html')


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта', category='green')
    return redirect(url_for('login'))


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        data = dict(request.form)

        err = False

        id_user = current_user.get_id()
        date = data.get('booking_datetime')

        if not data.get('auto'):
            err = True
            flash('Заполните авто', category='red')
        
        elif not data.get('problem'):
            err = True
            flash('Заполните проблему', category='red')
        

        elif not date:
            err = True
            flash('Заполните дату', category='red')
        
        elif not err:
            datetime_object = datetime.strptime(date, '%Y-%m-%dT%H:%M')
            if datetime_object.time() < datetime.strptime('08:00', '%H:%M').time() or datetime_object.time() > datetime.strptime('21:00', '%H:%M').time():
                err = True
                flash('Укажите время с 8:00 до 21:00', category='red')
        
        if not err:
            req = Request(
                id_user=id_user,
                auto=data.get('auto'),
                problem=data.get('problem'),
                booking_datetime=date,
                id_status=1
            )
            db.session.add(req)
            db.session.commit()

            flash('Ваша заявка принята', category='green')
        
    id_user = current_user.get_id()
    user = User.query.filter_by(id=id_user).first()
    requests = Request.query.filter_by(id_user=id_user).all()

    return render_template('index.html', user=user, requests=requests)
    

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    id_role = current_user.role.id

    if id_role != 2:
        flash('У вас недостаточно прав', category='red')
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = dict(request.form)
        id_request = data.get('id_request')
        id_status = data.get('id_status')

        req = Request.query.get(id_request)
        req.id_status = id_status

        db.session.commit()
        

    requests = Request.query.all()
    statuses = Status.query.all()
    return render_template('admin.html', requests=requests, statuses=statuses)


# ===================
#  Запуск приложения
# ===================

app.run(debug=True)