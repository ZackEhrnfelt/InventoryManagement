from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, FileField, IntegerField, SubmitField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length
from app.models import User

TextField = StringField

class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')

class LogoutForm(FlaskForm):
    submit = SubmitField('Sign Out')

class CreateAccountForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    username = TextField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    userdescription = TextField('Description', validators=[DataRequired()], render_kw={"placeholder": "Please Enter A Short Description About Yourself"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Create Account')
    
class CreateItemForm(FlaskForm):
    Itemname = StringField('Item Name', validators=[DataRequired()], render_kw={"placeholder": "Enter Item Name:"})
    Itemdescription = TextAreaField('Description', validators=[DataRequired()], render_kw={"placeholder": "Enter or Paste Question Here:", "rows": 15, "cols": 11})
    submit = SubmitField('Create Item')

class DeleteItemForm(FlaskForm):
    Itemname = StringField('Item Name', validators=[DataRequired()], render_kw={"placeholder": "Enter Item Name:"})
    submit = SubmitField('Delete Item')

class SearchItemForm(FlaskForm):
    Itemname = StringField('Item Name', validators=[DataRequired()], render_kw={"placeholder": "Enter Item Name:"})
    submit = SubmitField('Search Item')

    
class PostForm(FlaskForm):
    post = StringField('post', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
   # about_me = TextAreaField('about_me', [validators.length(max=140)])
    search_name = TextAreaField('Searchbox')

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append('This nickname is already in use. '
                                        'Please choose another one.')
            return False
        return True
        
class Searchbox(FlaskForm):
    search = StringField('search', validators=[DataRequired()])

class SendEmailForm(FlaskForm):
    email = StringField('Recipient: ',  validators=[DataRequired()], render_kw={"placeholder": "Please Enter or Paste Our Email Here:"})
    subject = StringField('Subject: ',  validators=[DataRequired()], render_kw={"placeholder": "Please Enter Email Subject Here:"})
    message = TextAreaField('Your Message:',  validators=[DataRequired()], render_kw={"placeholder": "Ask Your Questions Here:"})
    submit = SubmitField('Send')    

class InventoryItemForm(FlaskForm):
    name = TextField('Item Name: ', validators=[DataRequired()], render_kw={"placeholder": "Name"})
    item_number = TextField('Item Number: ', validators=[DataRequired()], render_kw={"placeholder": "Item Number"})
    voltage = IntegerField('Voltage: ', validators=[DataRequired()], render_kw={"placeholder": "Voltage"})
    description = TextAreaField('Description: ',  validators=[DataRequired()], render_kw={"placeholder": "Description"})
    manufacturer = TextField('Manufacturer: ', validators=[DataRequired()], render_kw={"placeholder": "Manufacturer"})
    price = IntegerField('Price: ', validators=[DataRequired()], render_kw={"placeholder": "Price ($)"})
    location = TextField('Location : ', validators=[DataRequired()], render_kw={"placeholder": "Location"})
    submit = SubmitField('Save')

    def set_data(self, data):
        self.name.data = data.name
        self.item_number.data = data.item_number
        self.voltage.data = data.voltage
        self.description.data = data.description
        self.manufacturer.data = data.manufacturer
        self.price.data = data.price
        self.location.data = data.location

class ImageUploadForm(FlaskForm):
    image = FileField('Photo', validators=[DataRequired()], render_kw={"placeholder": "Upload Image"})
    
    def set_data(self, data):
        self.image.data = data.image


class MailForm(FlaskForm):
    mail_to = TextField('Mail To: ', validators=[DataRequired()], render_kw={"placeholder": "Recepient"})
    subject = TextField('Subject: ', validators=[DataRequired()], render_kw={"placeholder": "Subject"})
    body = TextAreaField('Mail Body: ', validators=[DataRequired()], render_kw={"placeholder": "Mail Body"})
    submit = SubmitField('Send Mail')