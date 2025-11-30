import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from datetime import datetime
from enum import Enum
from flask import flash, redirect, url_for, request
from flask_login import login_required, current_user

# --- 1. 애플리케이션 및 DB 설정 ---

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_that_should_be_changed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    basedir, 'caravan_share.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login이 사용자 ID를 기반으로 사용자를 로드하는 함수"""
    return db.session.get(User, int(user_id))


# --- 2. 도메인 모델 정의 (리뷰 시스템 반영) ---


class UserRole(Enum):
    GUEST = 'guest'
    HOST = 'host'


class CaravanStatus(Enum):
    AVAILABLE = 'available'
    BOOKED = 'booked'
    MAINTENANCE = 'maintenance'


class ReservationStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'  # 🚨 [추가] 거래 완료 상태


class User(db.Model, UserMixin):
    """사용자 정보 모델 (DB 테이블) - 리뷰 평점 필드 추가"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    user_role = db.Column(db.Enum(UserRole),
                          default=UserRole.GUEST,
                          nullable=False)

    # 🚨 [수정] 호스트/게스트 역할별 평점 및 카운트 추가
    average_host_rating = db.Column(db.Float, default=0.0)
    host_review_count = db.Column(db.Integer, default=0)
    average_guest_rating = db.Column(db.Float, default=0.0)
    guest_review_count = db.Column(db.Integer, default=0)
    balance = db.Column(db.Float, default=0.0, nullable=False)

    caravans = db.relationship('Caravan', backref='host', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Caravan(db.Model):
    """카라반 정보 모델 - 리뷰 평점 필드 추가"""
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(CaravanStatus), default=CaravanStatus.AVAILABLE)

    # 🚨 [수정] 카라반 자체의 평점 및 카운트 추가
    average_rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)


class Reservation(db.Model):
    """예약 정보 모델 - 리뷰 플래그 추가"""
    id = db.Column(db.Integer, primary_key=True)
    caravan_id = db.Column(db.Integer,
                           db.ForeignKey('caravan.id'),
                           nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(ReservationStatus),
                       default=ReservationStatus.PENDING)

    # 🚨 [추가] 리뷰 작성 여부 플래그
    guest_reviewed = db.Column(db.Boolean, default=False)

    caravan = db.relationship('Caravan', backref='reservations')
    guest = db.relationship('User', backref='reservations')


class Review(db.Model):
    """리뷰/평가 정보 모델"""
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer,
                               db.ForeignKey('reservation.id'),
                               nullable=False)

    # 누가 리뷰를 작성했는지 (게스트)
    reviewer_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            nullable=False)
    # 리뷰의 대상 (호스트)
    reviewed_user_id = db.Column(db.Integer,
                                 db.ForeignKey('user.id'),
                                 nullable=False)

    caravan_id = db.Column(db.Integer,
                           db.ForeignKey('caravan.id'),
                           nullable=False)

    rating = db.Column(db.Integer, nullable=False)  # 1-5점
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 관계 정의 (외래 키가 여러 개인 경우 foreign_keys 명시)
    reservation = db.relationship('Reservation',
                                  backref='reviews',
                                  foreign_keys=[reservation_id])
    reviewer = db.relationship('User',
                               foreign_keys=[reviewer_id],
                               backref='reviews_given')
    reviewed_user = db.relationship('User',
                                    foreign_keys=[reviewed_user_id],
                                    backref=db.backref('reviews_received',
                                                       lazy='dynamic'))
    caravan = db.relationship('Caravan',
                              backref=db.backref('caravan_reviews',
                                                 lazy='dynamic'),
                              foreign_keys=[caravan_id])


# --- 3. WTForms 정의 ---


class RegistrationForm(FlaskForm):
    """회원가입 폼"""
    # ... (기존 코드 유지)
    name = StringField('이름',
                       validators=[DataRequired(),
                                   Length(min=2, max=100)])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호',
                             validators=[DataRequired(),
                                         Length(min=6)])
    confirm_password = PasswordField('비밀번호 확인',
                                     validators=[
                                         DataRequired(),
                                         EqualTo('password',
                                                 message='비밀번호가 일치하지 않습니다.')
                                     ])
    role = SelectField('역할',
                       choices=[(UserRole.GUEST.value, '게스트 (이용자)'),
                                (UserRole.HOST.value, '호스트 (소유자)')],
                       validators=[DataRequired()])
    submit = SubmitField('가입하기')

    def validate_email(self, field):
        """이메일 중복 확인"""
        if db.session.execute(db.select(User).filter_by(
                email=field.data)).scalar_one_or_none():
            raise ValidationError('이미 등록된 이메일 주소입니다.')


class LoginForm(FlaskForm):
    """로그인 폼"""
    # ... (기존 코드 유지)
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    remember = BooleanField('아이디 기억하기')
    submit = SubmitField('로그인')


class CaravanRegistrationForm(FlaskForm):
    """카라반 등록 폼"""
    # ... (기존 코드 유지)
    name = StringField('카라반 이름', validators=[DataRequired(), Length(max=100)])
    location = StringField('위치 (도시, 지역)',
                           validators=[DataRequired(),
                                       Length(max=100)])
    daily_rate = FloatField('1일 요금 (KRW)',
                            validators=[DataRequired(),
                                        NumberRange(min=1000)])
    capacity = IntegerField('수용 인원',
                            validators=[DataRequired(),
                                        NumberRange(min=1)])
    description = TextAreaField('설명', validators=[DataRequired()])
    submit = SubmitField('카라반 등록하기')


class ProfileEditForm(FlaskForm):
    """프로필 수정 폼"""
    # ... (기존 코드 유지)
    name = StringField('이름',
                       validators=[DataRequired(),
                                   Length(min=2, max=100)])
    contact = StringField('연락처')
    submit = SubmitField('수정 완료')


class CaravanSearchForm(FlaskForm):
    """카라반 검색 폼"""
    # ... (기존 코드 유지)
    location = StringField('위치', validators=[DataRequired()])
    start_date = StringField('체크인 날짜', validators=[DataRequired()])
    end_date = StringField('체크아웃 날짜', validators=[DataRequired()])
    submit = SubmitField('카라반 검색')


class ReservationForm(FlaskForm):
    """카라반 예약 폼"""
    # ... (기존 코드 유지)
    start_date = DateField('체크인 날짜',
                           format='%Y-%m-%d',
                           validators=[DataRequired()])
    end_date = DateField('체크아웃 날짜',
                         format='%Y-%m-%d',
                         validators=[DataRequired()])
    submit = SubmitField('예약 신청 및 결제')

    def validate_end_date(self, field):
        """종료일이 시작일보다 빠르거나 같지 않은지 검사"""
        if field.data <= self.start_date.data:
            raise ValidationError('종료일은 시작일보다 늦어야 합니다.')


class ReviewForm(FlaskForm):
    """리뷰 작성 폼"""
    rating = SelectField('평점 (1-5점)',
                         choices=[(5, '5점 - 최고'), (4, '4점 - 좋음'),
                                  (3, '3점 - 보통'), (2, '2점 - 나쁨'),
                                  (1, '1점 - 최악')],
                         coerce=int,
                         validators=[DataRequired()])
    comment = TextAreaField('리뷰 내용',
                            validators=[DataRequired(),
                                        Length(max=500)])
    submit = SubmitField('리뷰 제출')


# 🚨 [추가] 평점 계산 헬퍼 함수
def update_user_rating(user_id, is_host_rating=True):
    """특정 사용자가 받은 모든 리뷰를 기반으로 평균 평점과 리뷰 수를 업데이트합니다."""

    # 1. 대상 사용자가 받은 모든 리뷰를 조회
    reviews = Review.query.filter_by(reviewed_user_id=user_id).all()
    user = User.query.get(user_id)

    if reviews:
        total_score = sum(r.rating for r in reviews)
        count = len(reviews)
        new_average = total_score / count

        # 2. User 모델 업데이트
        if is_host_rating:
            # 호스트로서의 평점 업데이트 (게스트로부터 받은 리뷰)
            user.average_host_rating = round(new_average, 2)
            user.host_review_count = count
        else:
            # 게스트로서의 평점 업데이트 (호스트로부터 받은 리뷰)
            user.average_guest_rating = round(new_average, 2)
            user.guest_review_count = count

        db.session.commit()
    elif is_host_rating:
        # 리뷰가 없으면 0으로 초기화
        user.average_host_rating = 0.0
        user.host_review_count = 0
        db.session.commit()
    # 게스트 평점은 호스트가 리뷰를 작성해야 계산되므로 여기서는 무시


class AdminDepositForm(FlaskForm):
    """관리자가 특정 게스트에게 잔액을 충전하는 폼"""
    user_id = IntegerField('충전 대상 게스트 ID', validators=[DataRequired()])
    amount = FloatField('충전 금액 (KRW)',
                        validators=[DataRequired(),
                                    NumberRange(min=1000)])
    submit = SubmitField('잔액 충전 실행')


# --- 4. 라우트 정의 ---


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', title='CaravanShare 메인')


# ... (register, login, logout, dashboard 라우트 생략 - 기존과 동일)


@app.route('/users/register', methods=['GET', 'POST'])
def register():
    # ... (기존 코드 유지)
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    name=form.name.data,
                    user_role=UserRole(form.role.data))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='회원가입', form=form)


@app.route('/users/login', methods=['GET', 'POST'])
def login():
    # ... (기존 코드 유지)
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).filter_by(
                email=form.email.data)).scalar_one_or_none()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('로그인 성공!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('dashboard'))
        else:
            flash('로그인 실패: 이메일 또는 비밀번호를 확인해 주세요.', 'danger')

    return render_template('login.html', title='로그인', form=form)


@app.route('/users/logout')
@login_required
def logout():
    # ... (기존 코드 유지)
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # ... (기존 코드 유지)
    return render_template('dashboard.html', title='대시보드', user=current_user)


@app.route('/caravans/search', methods=['GET', 'POST'])
@login_required
def search_caravans():
    # ... (기존 코드 유지)
    form = CaravanSearchForm()
    caravans = []

    if form.validate_on_submit():
        location_query = form.location.data
        caravans = Caravan.query.filter(
            Caravan.location.contains(location_query)).all()
        flash(f"'{location_query}' 지역에서 {len(caravans)}개의 카라반을 찾았습니다.", 'info')

    else:
        all_caravans = Caravan.query.all()
        caravans = all_caravans

        print(f"--- [DEBUG] DB 조회 결과: 총 {len(all_caravans)}개 ---")
        if all_caravans:
            print(
                f"첫 번째 카라반: ID={all_caravans[0].id}, 이름={all_caravans[0].name}, 위치={all_caravans[0].location}"
            )

    return render_template('search_caravans.html',
                           title='카라반 검색',
                           form=form,
                           caravans=caravans)


@app.route('/caravans/<int:caravan_id>', methods=['GET'])
def caravan_detail(caravan_id):
    """카라반 상세 정보를 보여주는 라우트"""
    caravan = Caravan.query.get_or_404(caravan_id)
    form = ReservationForm()

    return render_template('caravan_detail.html',
                           title=f"{caravan.name} 상세 정보",
                           caravan=caravan,
                           form=form)


@app.route('/reservations/new/<int:caravan_id>', methods=['GET', 'POST'])
@login_required
def reserve_caravan(caravan_id):
    # ... (기존 코드 유지)
    caravan = Caravan.query.get_or_404(caravan_id)
    form = ReservationForm()

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        # 🚨 [핵심 로직] 중복 예약 확인
        conflicting_reservations = Reservation.query.filter(
            Reservation.caravan_id == caravan_id,
            Reservation.status == ReservationStatus.CONFIRMED,
            Reservation.start_date < end_date, Reservation.end_date
            > start_date).count()

        if conflicting_reservations > 0:
            flash("선택하신 기간에는 이미 확정된 예약이 있어 신청할 수 없습니다.", 'danger')
            return redirect(url_for('caravan_detail', caravan_id=caravan_id))

        # 가격 계산
        duration_days = (end_date - start_date).days
        total_price = duration_days * caravan.daily_rate

        # Reservation 객체 생성 및 DB 저장
        new_reservation = Reservation(
            caravan_id=caravan_id,
            guest_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status=ReservationStatus.PENDING  # 일단 승인 대기로 저장
        )
        db.session.add(new_reservation)
        db.session.commit()

        flash(f"예약 신청이 완료되었습니다. 총 {total_price:,.0f} KRW이며, 호스트 승인 대기 중입니다.",
              'success')
        return redirect(url_for('reservations_guest'))

    flash("예약 날짜를 다시 확인해 주세요.", 'warning')
    return redirect(url_for('caravan_detail', caravan_id=caravan_id))


@app.route('/reservations/my', methods=['GET'])
@login_required
def reservations_guest():
    """내 예약 현황 (게스트) 라우트"""
    # 게스트의 모든 예약 정보 조회 로직
    reservations = Reservation.query.filter_by(guest_id=current_user.id).all()
    return render_template('reservations.html',
                           title='내 예약 현황',
                           reservations=reservations)


@app.route('/reservations/host', methods=['GET'])
@login_required
def reservations_host():
    # ... (기존 코드 유지)
    host_caravan_ids = [c.id for c in current_user.caravans]

    if not host_caravan_ids:
        flash("등록된 카라반이 없습니다. 먼저 카라반을 등록해주세요.", 'warning')
        return render_template('reservations_host.html',
                               title='예약 관리 (호스트)',
                               reservations=[])

    host_reservations = Reservation.query.filter(
        Reservation.caravan_id.in_(host_caravan_ids)).all()

    return render_template('reservations_host.html',
                           title='예약 관리 (호스트)',
                           reservations=host_reservations)


# ... (edit_profile, register_caravan 라우트 생략 - 기존과 동일)


@app.route('/users/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # ... (기존 코드 유지)
    form = ProfileEditForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.contact = form.contact.data
        db.session.commit()
        flash('프로필 정보가 업데이트되었습니다.', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        form.name.data = current_user.name
        form.contact.data = current_user.contact

    return render_template('profile.html', title='프로필 수정', form=form)


@app.route('/caravans/new', methods=['GET', 'POST'])
@login_required
def register_caravan():
    # ... (기존 코드 유지)
    form = CaravanRegistrationForm()
    if form.validate_on_submit():
        caravan = Caravan(host_id=current_user.id,
                          name=form.name.data,
                          location=form.location.data,
                          daily_rate=form.daily_rate.data,
                          capacity=form.capacity.data,
                          description=form.description.data)
        db.session.add(caravan)
        db.session.commit()
        flash('카라반 등록이 완료되었습니다.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register_caravan.html', title='카라반 등록', form=form)


# 🚨 [승인/거절 라우트 - 완료 상태 추가]
@app.route('/reservations/approve/<int:reservation_id>')
@login_required
def approve_reservation(reservation_id):
    """예약 승인 처리"""
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.caravan.host_id != current_user.id:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('reservations_host'))

    if reservation.status != ReservationStatus.PENDING:
        flash('이미 처리되었거나 취소된 예약입니다.', 'warning')
    else:
        reservation.status = ReservationStatus.CONFIRMED
        db.session.commit()
        flash(f'예약 #{reservation_id}가 승인되었습니다.', 'success')

    return redirect(url_for('reservations_host'))


@app.route('/reservations/reject/<int:reservation_id>')
@login_required
def reject_reservation(reservation_id):
    """예약 거절 처리"""
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.caravan.host_id != current_user.id:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('reservations_host'))

    if reservation.status != ReservationStatus.PENDING:
        flash('이미 처리되었거나 취소된 예약입니다.', 'warning')
    else:
        reservation.status = ReservationStatus.CANCELLED
        reservation.caravan.status = CaravanStatus.AVAILABLE
        db.session.commit()

    return redirect(url_for('reservations_host'))


@app.route('/reservations/complete/<int:reservation_id>')
@login_required
def complete_reservation(reservation_id):
    """예약 완료 처리 (실제 거래 종료)"""
    reservation = Reservation.query.get_or_404(reservation_id)

    # 호스트만 완료 처리 가능
    if reservation.caravan.host_id != current_user.id:
        flash('권한이 없습니다.', 'danger')
        return redirect(url_for('reservations_host'))

    if reservation.status != ReservationStatus.CONFIRMED:
        flash('확정되지 않은 예약은 완료할 수 없습니다.', 'warning')
    else:
        # 거래 완료 상태로 변경
        reservation.status = ReservationStatus.COMPLETED
        db.session.commit()
        flash(f'예약 #{reservation_id}가 완료 상태로 변경되었습니다. 이제 게스트는 리뷰를 작성할 수 있습니다.',
              'success')

    return redirect(url_for('reservations_host'))


# 🚨 [리뷰 작성 라우트]
@app.route('/reservations/<int:reservation_id>/review',
           methods=['GET', 'POST'])
@login_required
def write_review(reservation_id):
    """특정 예약에 대한 리뷰 작성 페이지"""
    reservation = Reservation.query.get_or_404(reservation_id)
    form = ReviewForm()

    # 1. 리뷰 권한 및 상태 확인 (게스트만 작성 가능 & 거래 완료 상태에서만 가능)
    if reservation.guest_id != current_user.id:
        flash("리뷰 작성 권한이 없습니다.", 'danger')
        return redirect(url_for('reservations_guest'))

    if reservation.status != ReservationStatus.COMPLETED:
        flash("거래가 완료되지 않은 예약은 리뷰를 작성할 수 없습니다.", 'danger')
        return redirect(url_for('reservations_guest'))

    if reservation.guest_reviewed:
        flash("이미 리뷰를 작성하셨습니다.", 'warning')
        return redirect(url_for('reservations_guest'))

    if form.validate_on_submit():
        # 2. 리뷰 대상 결정 (게스트가 호스트와 카라반을 리뷰)
        reviewed_host = reservation.caravan.host

        # 3. 리뷰 객체 생성 및 저장
        new_review = Review(reservation_id=reservation_id,
                            reviewer_id=current_user.id,
                            reviewed_user_id=reviewed_host.id,
                            caravan_id=reservation.caravan_id,
                            rating=form.rating.data,
                            comment=form.comment.data)
        db.session.add(new_review)

        # 4. 리뷰 작성 완료 플래그 설정
        reservation.guest_reviewed = True

        db.session.commit()  # 리뷰 객체와 플래그를 DB에 먼저 저장

        # 5. 평점 업데이트 로직 실행 (호스트의 평점 업데이트)
        update_user_rating(reviewed_host.id, is_host_rating=True)

        flash("리뷰가 성공적으로 제출되었습니다!", 'success')
        return redirect(url_for('reservations_guest'))

    return render_template('review_form.html',
                           title='리뷰 작성',
                           form=form,
                           reservation=reservation)


@app.route('/deposit', methods=['POST'])
@login_required
def deposit():
    """현재 로그인된 사용자의 잔액을 충전하는 기능 (POST 요청 처리)"""
    # 현재 로그인된 사용자만 접근 가능하도록 합니다.
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # 폼 데이터에서 'amount' 값을 가져와 float형으로 변환합니다.
            amount = float(request.form.get('amount'))

            # 금액이 양수인지 검증합니다.
            if amount <= 0:
                flash('충전 금액은 양수여야 합니다.', 'danger')
                return redirect(url_for('dashboard'))

            # 현재 사용자의 잔액을 업데이트하고 DB에 커밋합니다.
            current_user.balance += amount
            db.session.commit()

            # 성공 메시지를 띄우고 대시보드로 리다이렉트합니다.
            # 금액에 콤마를 넣어 더 보기 좋게 만듭니다.
            flash(f'잔액이 성공적으로 충전되었습니다. 충전 금액: ₩{amount:,.0f}', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            # 숫자가 아닌 값이 입력된 경우
            flash('유효한 금액(숫자)을 입력해 주세요.', 'danger')
        except Exception as e:
            # 기타 DB 또는 서버 오류 발생 시
            flash(f'충전 중 오류가 발생했습니다: {e}', 'danger')
            db.session.rollback()  # 오류 발생 시 DB 변경사항을 되돌립니다.

    # POST 요청이 아닌 경우 (또는 오류 처리 후) 대시보드로 리다이렉트합니다.
    return redirect(url_for('dashboard'))


# main.py 파일의 라우트 정의 섹션에 추가 (기존 deposit_funds 대체)


@app.route('/admin/deposit', methods=['GET', 'POST'])
@login_required
def admin_deposit():
    """관리자/호스트가 특정 게스트의 잔액을 충전하는 UI 및 로직"""
    # 호스트만 접근 가능하도록 합니다.
    if current_user.user_role != UserRole.HOST:
        flash("권한이 없습니다. 호스트만 잔액을 관리할 수 있습니다.", 'danger')
        return redirect(url_for('dashboard'))

    form = AdminDepositForm()

    if form.validate_on_submit():
        user_to_update = User.query.get(form.user_id.data)
        amount = form.amount.data

        if not user_to_update or user_to_update.user_role != UserRole.GUEST:
            flash(f"ID {form.user_id.data}는 유효한 게스트 계정이 아닙니다.", 'danger')
            return redirect(url_for('admin_deposit'))

        # 잔액 충전 로직
        user_to_update.balance += amount
        db.session.commit()

        flash(
            f"{user_to_update.name} 님에게 ₩{amount:,.0f} KRW가 충전되었습니다. 현재 잔액: ₩{user_to_update.balance:,.0f}",
            'success')
        return redirect(url_for('dashboard'))

    # GET 요청 또는 폼 오류 시 템플릿 렌더링
    return render_template('admin_deposit.html', title='게스트 잔액 충전', form=form)


# --- 5. 앱 실행 ---

import os  # os 모듈이 import 되어 있어야 합니다.

# Replit 환경 변수 PORT를 사용하고, 없을 경우 5000(또는 8080)을 기본값으로 사용
PORT = int(os.environ.get('PORT', 8080))

if __name__ == '__main__':
    # 🚨 [수정된 부분] 🚨
    # 서버가 시작되기 전에 db.create_all()을 실행하는 대신,
    # Flask 앱 실행 환경에서 db.create_all()이 자동으로 실행되도록 설정하는 것이 안전합니다.

    # 1. db.create_all() 코드는 그대로 유지합니다.
    with app.app_context():
        db.create_all()

    # 2. 서버 실행
    app.run(host='0.0.0.0', port=PORT, debug=True)
