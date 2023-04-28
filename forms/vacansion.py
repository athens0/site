from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FileField
from wtforms.validators import DataRequired


class CreateForm(FlaskForm):
    job = StringField('Должность', validators=[DataRequired()])
    year = IntegerField('Стаж работы', validators=[DataRequired()])
    desc = StringField('Коротко о вас и о ваших навыках', validators=[DataRequired()])
    photo = FileField('Ваше фото', validators=[DataRequired()])
    submit = SubmitField('Отправить')