from locale import currency
from flask import render_template, url_for, redirect, g, request, session, url_for, redirect, render_template, jsonify
from functools import wraps
import os
from werkzeug.utils import secure_filename
import redis
import json
import time


from . import site
from ..models import db, User, Message, User_api_company, User_api_details, User_api_urls, User_catalogue
from ..forms import NameForm
from ..database import get_all, add_instance, delete_instance, edit_instance
import hashlib
from ..api import AlchemyEncoder
from ..api.holigest import Holigest
from ..api import api


redis_url = os.getenv('REDISTOGO_URL', os.environ['REDIS_URL'])
redis_client = redis.from_url(redis_url)
print("redis client connected " + str(redis_client))


# custom 404 handler
@site.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def authorize(f):
    @wraps(f)
    def login_required(*args, **kws):
        user_id = session.get("user_id")
        if g.user is None:
            return redirect(url_for("auth.login"))
    return login_required

def login_check():
    if g.user is None:
        return redirect(url_for("auth.login"))
    return True

@site.route('/', methods=['GET', 'POST'])
def index():
    error = None
    # name = None
    # new = False
    # form = NameForm()
    # if form.validate_on_submit():
    #     name = form.name.data
    #     description = form.description.data
    #     form.name.data = ''
    #     form.description.data = ''
    #     if User.query.filter_by(name=name).first() is None:
    #         db.session.add(User(name=name, description=description))
    #         db.session.commit()
    #         new = True
    response = get_all()
 
    if response['user'] == None:
        return redirect(url_for("auth.login"))

    return render_template('site/index.html', user=response['user'], api_details=response['api_details'], api_companies=response['api_companies'], error=error)

@site.route('/site/catalogue', methods=['GET', 'POST'])
def catalogue():
    error = None
    # name = None
    # new = False
    # form = NameForm()
    # if form.validate_on_submit():
    #     name = form.name.data
    #     description = form.description.data
    #     form.name.data = ''
    #     form.description.data = ''
    #     if User.query.filter_by(name=name).first() is None:
    #         db.session.add(User(name=name, description=description))
    #         db.session.commit()
    #         new = True
    response = get_all()
    
    return render_template('site/catalogue.html', user=response['user'], api_details=response['api_details'], api_companies=response['api_companies'], user_catalogue=response['user_catalogue'], show_catalogue=show_catalogue, error=error)

# update catalogue 
# ImmutableMultiDict([('user_id', '1'), ('counter', '17'), ('phone_number', '917893273022'), ('phone_number_encrypted', '37470c9583a8de5932b3f944391edb54'), ('email', 'dhiraj.patra@gmail.com'), ('property_id_1', '7'), ('property_name_1', 'Apt B - Wellness House Galilei 3 sleeps'), ('id_ru_1', '1691658'), ('link_1', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-3-sleeps---apt-b----7'), ('price_1', '42.0'), ('currency_1', 'EUR'), ('property_id_2', '9'), ('property_name_2', 'Apt D - Wellnes House Galilei 6 sleeps '), ('id_ru_2', '1691660'), ('link_2', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-6-sleeps---apt-d-9'), ('price_2', '74.0'), ('currency_2', 'EUR'), ('property_id_3', '6'), ('property_name_3', 'Apt A - Wellness House Galilei 5 sleeps'), ('id_ru_3', '1691657'), ('link_3', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-galilei-apt-a---5-sleeps-6'), ('price_3', '55.0'), ('currency_3', 'EUR'), ('property_id_4', '10'), ('property_name_4', 'Apt F - Wellness House Galilei 14 Sleeps'), ('id_ru_4', '1691662'), ('link_4', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-14-sleeps---apt-f----10'), ('price_4', '84.0'), ('currency_4', 'EUR'), ('property_id_5', '8'), ('property_name_5', 'Apt C - Wellness Hose Galilei 8 sleeps'), ('id_ru_5', '1691659'), ('link_5', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-8-sleeps---apt-c----8'), ('price_5', '136.0'), ('currency_5', 'EUR'), ('property_id_6', '5'), ('property_name_6', 'Giardino Tropicale Eco-friendly accomodation, wide tropical garden, by the sea'), ('id_ru_6', '2165412'), ('link_6', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/giardino-tropicale---350-mt-from-beach-wide-garden-5'), ('price_6', '122.0'), ('currency_6', 'EUR'), ('property_id_7', '2'), ('property_name_7', 'Apt E - Wellness Hose Galilei 9 sleeps'), ('id_ru_7', '1115731'), ('link_7', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/wellness-house-galilei-9-sleeps---apt-e----2'), ('price_7', '94.0'), ('currency_7', 'EUR'), ('property_id_8', '4'), ('property_name_8', 'Giardino di Limoni Eco friendly Villa close to the beach'), ('id_ru_8', '1144860'), ('link_8', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/villa-giardino-di-limoni-4'), ('price_8', '245.0'), ('currency_8', 'EUR'), ('property_id_9', '3'), ('property_name_9', 'Casale della Pergola Eco friendly firm house by the sea '), ('id_ru_9', '1144798'), ('link_9', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/casale-della-pergola-3'), ('price_9', '122.0'), ('currency_9', 'EUR'), ('property_id_10', '1'), ('property_name_10', 'Apartment Eucaliptus sea view terrace, 40 mt from sea'), ('id_ru_10', '1132672'), ('link_10', 'https://www.hiresicily.com/holiday-apartments-noto-syracuse/apartment-eucaliptus-sea-view-forty-mt-from-beach-1'), ('price_10', '88.0'), ('currency_10', 'EUR'), ('price_11', '100'), ('currency_11', 'EUR'), ('price_12', ''), ('currency_12', 'EUR'), ('price_13', ''), ('currency_13', 'EUR'), ('price_14', ''), ('currency_14', 'EUR'), ('price_15', ''), ('currency_15', 'EUR'), ('price_16', ''), ('currency_16', 'EUR'), ('price_17', ''), ('currency_17', 'EUR')])
@site.route('/site/catalogue_update', methods=['GET', 'POST'])
def catalogue_update():
    error = None
    response = get_all()
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        counter = int(request.form['counter'])
        
        for i in range(1, counter):
            if request.form['property_id_' + str(i)] != '':
                catalogue_image = ''
                # check if the post request has the file part
                if 'catalogue_image_' + str(i)  not in request.files:
                    error = 'No file part'
                    print(error)
                    return redirect(request.url)
                file = request.files['catalogue_image_' + str(i)]
                print(str(file.filename))
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    error = 'No selected file'
                    print(error)
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    print('allowed')
                    curr_time = int(str(time.time()).replace('.', ''))
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(api.config['UPLOAD_FOLDER'], filename + curr_time))
                    catalogue_image = filename + curr_time
                    print(catalogue_image)

                property_id = request.form['property_id_' + str(i)]
                property_name = request.form['property_name_' + str(i)]
                id_ru = request.form['id_ru_' + str(i)]
                link = request.form['link_' + str(i)]
                price = request.form['price_' + str(i)]
                currency = request.form['currency_' + str(i)]
                print(price) 

                # delete the existing records for this user
                try:
                    # user_catalogue = User_catalogue.query.filter_by(user_id=user_id, id_ru=id_ru).delete()
                    # db.session.commit()

                    new_user_catalogue = User_catalogue(user_id=user_id, catalogue_image=catalogue_image, property_id=property_id, property_name=property_name, id_ru=id_ru, link=link, price=price, currency=currency)
                    db.session.add(new_user_catalogue)
                    db.session.commit()
                except:
                    db.session.rollback()
                finally:
                    # db.session.close()
                    pass
                 

    
    return render_template('site/catalogue.html', user=response['user'], api_details=response['api_details'], api_companies=response['api_companies'], user_catalogue=response['user_catalogue'], show_catalogue=show_catalogue, error=error)


@site.route('/users', methods=['GET'])
def users():
    login_check()
    users = User.query.all()
    return render_template('site/users.html', users=users)

@site.route('/users/<int:id>', methods=['GET'])
def user_details(id):
    login_check()
    user = User.query.get_or_404(id)
    return render_template('site/user_details.html', user=user)

@site.route('/users/delete/<int:id>', methods=['POST'])
def user_delete(id):
    login_check()
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('site.users'))

@site.route('/users/update/<int:id>', methods=['POST'])
def user_update(id):
    login_check()
    api_company_id = request.form['api_company']
    key = request.form['api_key']
    username = request.form['api_username']
    password = request.form['api_password']
    host = request.form['api_host']
    bot_token = request.form['bot_token']
    type_of_business = request.form['type_of_business']
    welcome_msg = request.form['welcome_msg']
    edit_instance(User_api_details, id, api_company_id=api_company_id, key=key, username=username, password=password, host=host, bot_token=bot_token, type_of_business=type_of_business, welcome_msg=welcome_msg)

    return redirect(url_for('site.index'))

@site.route('/apis', methods=['GET', 'POST'])
def apis():
    user_id = session.get("user_id")
    login_check()
    error = None

    if request.method == "POST":
        pass

    user = User.query.filter_by(id = user_id).first()
    api_details = User_api_details.query.filter_by(user_id=user.id).first()
    api_companies = User_api_company.query.all()
    api_urls = User_api_urls.query.filter_by(user_id=user.id).all()

    return render_template('site/api.html', user=user, api_details=api_details, api_companies=api_companies, api_urls=api_urls, error=error)

def show_catalogue(catalogue_image):
        path = request.host_url.strip("/") + url_for('static', filename='images/'+ catalogue_image)
        # path = path.replace('http:', 'https:') 
        # resp = make_response(open(path).read())
        # resp.content_type = "image/jpeg"
        return path

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in api.config['ALLOWED_EXTENSIONS']

def get_all():
    user_id = session.get("user_id")
    login_check()
    response = {}

    user_redis = redis_client.get('user')
    api_details_redis = redis_client.get('api_details')
    api_companies_redis = redis_client.get('api_companies')
    if user_redis == None or api_details_redis == None or api_companies_redis == None:
        user = User.query.filter_by(id=user_id).first()
        api_details = User_api_details.query.filter_by(user_id=user_id).first()
        api_companies = User_api_company.query.all()
        
        redis_client.set('user', json.dumps(user, cls=AlchemyEncoder), 3600)
        redis_client.set('api_details', json.dumps(api_details, cls=AlchemyEncoder), 3600)
        redis_client.set('api_companies', json.dumps(api_companies, cls=AlchemyEncoder), 3600)

        user_redis = json.loads(redis_client.get('user').decode('utf-8'))
        api_details_redis = json.loads(redis_client.get('api_details').decode('utf-8'))
        api_companies_redis = json.loads(redis_client.get('api_companies').decode('utf-8'))
    else:    
        user_redis = json.loads(redis_client.get('user').decode('utf-8'))
        api_details_redis = json.loads(redis_client.get('api_details').decode('utf-8'))
        api_companies_redis = json.loads(redis_client.get('api_companies').decode('utf-8'))

    
    # fetch all catalogue and keep in redis
    user_catalogue_redis = redis_client.get('user_catalogue')
    if user_catalogue_redis == None:
        user_catalogue = User_catalogue.query.filter_by(user_id=user_id).all()
        redis_client.set('user_catalogue', json.dumps(user_catalogue, cls=AlchemyEncoder), 3600)
        user_catalogue_redis = json.loads(redis_client.get('user_catalogue').decode('utf-8'))
    else:
        user_catalogue_redis = json.loads(redis_client.get('user_catalogue').decode('utf-8'))
    
    response['user'] = user_redis
    response['api_details'] = api_details_redis
    response['api_companies'] = api_companies_redis
    response['user_catalogue'] = user_catalogue_redis

    return response

