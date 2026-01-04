from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    prep_time = StringField('Prep Time (e.g., 15 mins)')
    cook_time = StringField('Cook Time (e.g., 30 mins)')
    servings = StringField('Servings (e.g., 4)')
    cuisine = SelectField('Cuisine', choices=[('', 'Select Cuisine'), ('Italian', 'Italian'), ('Chinese', 'Chinese'), ('Mexican', 'Mexican'), ('Indian', 'Indian'), ('Other', 'Other')])
    difficulty = SelectField('Difficulty', choices=[('', 'Select Difficulty'), ('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])
    tags = StringField('Tags (comma-separated)')
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
