import os

from sqlalchemy.sql.expression import asc
from app import app, mail
from config import MAX_SEARCH_RESULTS
from flask_mail import Mail, Message
from sqlalchemy import desc as DESC_SORT, asc as ASEC_SORT
from flask import render_template, redirect, url_for, flash, request, g, session
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import ImageUploadForm, InventoryItemForm, LoginForm, LogoutForm, CreateAccountForm, CreateItemForm, DeleteItemForm, MailForm, SearchItemForm,Searchbox, SendEmailForm
from app import db
from app.models import InventoryItem, User, Items
from datetime import datetime
from pytz import timezone
import sys

@app.route('/')
def index():
    items = InventoryItem.query.all()
    return render_template('index.html', items=items)

mail = Mail(app)

@app.route('/Contact', methods=['GET', 'POST'])
def contact():
    mail_form = SendEmailForm()
    if mail_form.validate_on_submit():
        recipient = mail_form.email.data
        message = mail_form.message.data
        subject = mail_form.subject.data
        msg = Message(subject = subject, recipients=[recipient], body = message)
        mail.send(msg)
        mail_form.email.data = ''
        mail_form.subject.data = ''
        mail_form.message.data = ''
    return render_template('Contact_Us.html', form=mail_form)
    
@app.before_request
def before_request():
    g.user = current_user
    tz = timezone('EST')
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = Searchbox()
        current_user.last_seen = datetime.now(tz)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Authenticated users are redirected to home page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        #Query Database for user by username
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            print('Login Failed', file=sys.stderr)
            return redirect(url_for('login'))
        #login_user is a flask_login function that starts a session
        login_user(user)
        print('Login Successful', file=sys.stderr)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    form = LogoutForm()
    if form.validate_on_submit():    
        logout_user()
        return redirect(url_for('login'))
    return render_template('logout.html', form=form)

def is_admin():

    if current_user:
        if current_user.role == 'admin':
            return True
        else:
            return False
    else:
        print('User not authenticated.', file=sys.stderr)


@app.route('/CreateAccount', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = CreateAccountForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user is None:
            email = form.email.data
            username = form.username.data
            userdescription = form.userdescription.data
            password = form.password.data  

            user = User(username=form.username.data, email=email, userdescription = form.userdescription.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)

            return redirect(url_for('index'))
    return render_template('CreateAccount.html', form=form)

@app.route('/edit-inventory-items/<int:id>', methods=['GET', 'POST'])
@app.route('/add-inventory-items', methods=['GET', 'POST'])
@login_required
def add_inventory_items(id=None): 
    form = InventoryItemForm(request.form)
    imgForm = ImageUploadForm(request.files)
    print(id)
    if request.method == 'GET' and id != None:
        data = InventoryItem.query.filter(InventoryItem.id == id).first()
        if data != None:
            form.set_data(data)
            imgForm.set_data(data)
    if form.validate_on_submit():
        print(imgForm.image.data)
        name = form.name.data
        item_number = form.item_number.data
        description = form.description.data
        voltage = form.voltage.data
        price = form.price.data
        location = form.location.data
        manufacturer = form.manufacturer.data
        if id == None and imgForm.image.data:
            image = request.files[imgForm.image.name]
            filename = current_user.username + ' - ' + name + ' - ' + item_number + '.' + imgForm.image.data.filename.split('.').pop()
            inventory_item = InventoryItem(name=name, voltage=voltage, item_number=item_number, location=location, price=price, manufacturer=manufacturer, description=description, user_id=current_user.get_id())
            image.save('app/static/inventory/' + filename)
            inventory_item.image = 'inventory/' + filename
            db.session.add(inventory_item)
        else:
            inventory_item = InventoryItem.query.filter(InventoryItem.id == id).first()
            inventory_item.name = form.name.data
            inventory_item.price = form.price.data
            inventory_item.location = form.location.data
            inventory_item.item_number = form.item_number.data
            inventory_item.voltage = form.voltage.data
            inventory_item.description = form.description.data
            inventory_item.manufacturer = form.manufacturer.data
            
            if imgForm.image.data:
                image = request.files[imgForm.image.name]
                filename = current_user.username + ' - ' + name + ' - ' + item_number + '.' + imgForm.image.data.filename.split('.').pop()
                os.remove('app/static/' + inventory_item.image)
                image.save('app/static/inventory/' + filename)
                inventory_item.image = 'inventory/' + filename

        db.session.commit()
        return redirect(url_for('view_inventory_items'))
    return render_template('Add_Inventory_Item.html', form=form, imgForm=imgForm)


@app.route('/view-inventory-items', methods=['GET'])
def view_inventory_items(): 
    items = InventoryItem.query
    name = request.args.get('name')
    price = request.args.get('price')
    sortby = request.args.get('sort')
    voltage = request.args.get('voltage')
    location = request.args.get('location')
    
    if name != None and name != '':
        items = items.filter(InventoryItem.name.contains(name))
    if price != None and price != '':
        items = items.filter(InventoryItem.price.between(0, price))
    if voltage != None and voltage != '':
        items = items.filter(InventoryItem.voltage.between(0, voltage))
    if location != None and location != '':
        items = items.filter(InventoryItem.location.contains(location))
    if sortby != None and sortby != '':
        if sortby == 'name_asc':
            items = items.order_by(InventoryItem.name.asc())
        elif sortby == 'name_desc':
            items = items.order_by(InventoryItem.name.desc())
        elif sortby == 'price_asc':
            items = items.order_by(InventoryItem.price.asc())
        elif sortby == 'price_desc':
            items = items.order_by(InventoryItem.price.desc())
        elif sortby == 'voltage_asc':
            items = items.order_by(InventoryItem.voltage.asc())
        elif sortby == 'voltage_desc':
            items = items.order_by(InventoryItem.voltage.desc())
        elif sortby == 'location_asc':
            items = items.order_by(InventoryItem.location.asc())
        elif sortby == 'location_desc':
            items = items.order_by(InventoryItem.location.desc())
        elif sortby == 'created_on_asc':
            items = items.order_by(InventoryItem.created_on.asc())
        elif sortby == 'created_on_desc':
            items = items.order_by(InventoryItem.created_on.desc())
        elif sortby == 'updated_on_asc':
            items = items.order_by(InventoryItem.updated_on.asc())
        elif sortby == 'updated_on_desc':
            items = items.order_by(InventoryItem.updated_on.desc())

    items = items.all()
    return render_template('View_Inventory_Item.html', items = items)


@app.route('/delete-inventory-items/<int:id>', methods=['GET'])
@login_required
def delete_inventory_item(id): 
    item = InventoryItem.query.filter(InventoryItem.id == id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('view_inventory_items'))


@app.route('/Admin', methods=['GET', 'POST'])
@login_required
def manageadmin():
    if is_admin():
        form = MailForm()
        return render_template('Manage_Admin.html', form=form)
    else:
        return redirect(url_for('index'))
        


@app.route('/user/<username>')
@login_required
def user(username):
    form = CreateAccountForm()
    user = db.session.query(User).filter_by(username=current_user.username, userdescription=current_user.userdescription).first()
    return render_template('Profile.html', user=user)
# @app.before_request
# def before_request():
#     tz = timezone('EST')
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.now(tz)
#         db.session.commit()

#     return render_template('Profile.html', groupnames=all)

@app.route('/CreateItem', methods=['GET', 'POST'])
@login_required
def createItem():
    form = CreateItemForm()  
    if form.validate_on_submit():
        Item_name = form.Itemname.data
        Itemdescription = form.Itemdescription.data    

        f = Items(Itemname=Item_name, Itemdescription=Itemdescription)

        db.session.add(f)
        db.session.commit()

        form.Itemname.data = ''
        form.Itemdescription.data =''
        return redirect(url_for('manageItem'))
    return render_template('Create_Item.html', form=form)

@app.route('/DeleteItem', methods=['GET', 'POST'])
def deleteItem():
    form = DeleteItemForm()
    if form.validate_on_submit():
        delete_Item = db.session.query(Items).filter_by(Itemname = form.Itemname.data).first()

        if delete_Item is not None:
            db.session.delete(delete_Item)
            db.session.commit()

        form.Itemname.data = ''
        return redirect(url_for('manageItem'))
    return render_template('Delete_Item.html', form=form)

@app.route('/SearchItem', methods=['GET', 'POST'])
def searchItem():
    form = SearchItemForm()
    if form.validate_on_submit():
        search_Item = db.session.query(Items).filter_by(Itemname = form.Itemname.data).all()

        if search_Item:
            return render_template('View_Items.html', Itemnames=search_Item)
        else:
            return render_template('Not_Found.html')
    return render_template('Search_Item.html', form=form)

@app.route('/ManageItem')
@login_required
def manageItem():
    return render_template('Manage_Item.html')

@app.route('/ViewItem')
def viewItem():
    all = db.session.query(Items).all()
    print(all, file=sys.stderr)
    return render_template('View_Items.html', Itemnames=all)
@app.route('/comment')
def comment():
    return render_template('comment.html')
    
@app.route('/Item/<Itemid>', methods=['GET', 'POST'])
def Item(Itemid):
    form=CommentForm()
    postid=Itemid
    if form.validate_on_submit():
        content = form.comment.data
        tz = timezone('EST')
        date = datetime.now(tz)
        user = db.session.query(User).filter_by(username=current_user.username).first()
        message = Comment(content=content, post_id=postid, user_id=user.username, date=date)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('Item', Itemid=Itemid))

    
    comments=db.session.query(Comment).filter_by(post_id=postid).all()
    print(all, file=sys.stderr)
    Item=db.session.query(Items).get(Itemid)
    return render_template('Item.html', Itemname=Item, comment=comment, comments=comments, form=form)




#Collects the search query then passes it as an argument.
@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('/'))
    return redirect(url_for('search_results', query=g.search_form.search.data))




#Send the query into Whoosh which then passes a max number of search results.
@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html', query=query, results=results)













