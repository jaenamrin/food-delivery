from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional



# -------------------------
# Форма регистрации
# -------------------------
class RegistrationForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[DataRequired(message="Введите имя пользователя"), Length(min=3, max=25)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(message="Введите email"), Email(message="Неверный формат email")]
    )
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(message="Введите пароль"), Length(min=6, message="Минимум 6 символов")]
    )
    submit = SubmitField('Зарегистрироваться')


# -------------------------
# Форма входа
# -------------------------
class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(message="Введите email"), Email(message="Неверный формат email")]
    )
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(message="Введите пароль")]
    )
    submit = SubmitField('Войти')

class ProfileForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Телефон', validators=[Optional(), Length(max=20)])
    address = StringField('Адрес', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Сохранить')

