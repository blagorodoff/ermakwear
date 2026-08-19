# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, FloatField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Введите логин')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Введите пароль')])
    submit = SubmitField('Войти')

class CollectionForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(message='Введите название коллекции')])
    description = StringField('Описание (лейбл)', validators=[Optional()])
    sort_order = IntegerField('Порядок сортировки', validators=[Optional(), NumberRange(min=0)], default=0)

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired(message='Введите название категории')])
    sort_order = IntegerField('Порядок сортировки', validators=[Optional(), NumberRange(min=0)], default=0)

class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired(message='Введите название товара')])
    price = FloatField('Цена (₽)', validators=[DataRequired(message='Введите цену'), NumberRange(min=0, message='Цена не может быть отрицательной')])
    collection_id = SelectField('Коллекция', coerce=int, validators=[DataRequired()])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    sort_order = IntegerField('Порядок сортировки', validators=[Optional(), NumberRange(min=0)], default=0)
    images = MultipleFileField('Фотографии товара (можно несколько)')