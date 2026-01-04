from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CommunityPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=120)])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Post')


class CommunityReplyForm(FlaskForm):
    content = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Reply')