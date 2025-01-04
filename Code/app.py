from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Admin, Sponsor, Influencer, Campaign, AdRequest
from datetime import datetime
from sqlalchemy import or_


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///adfusion.db'
db.init_app(app)


# Home Page
@app.route('/')
def index():
    return render_template('index.html')



## Now we will defining all the routing for User Registration process

# User Registration Page - First asks for user type then redirects to their specific Registration Page.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'admin':
            return redirect(url_for('admin_register'))
        elif role == 'sponsor':
            return redirect(url_for('sponsor_register'))
        elif role == 'influencer':
            return redirect(url_for('influencer_register'))

    return render_template('register.html')


# Admin Registration Page
@app.route('/admin-register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        new_admin = Admin(username=username, email=email, password=password)
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin registration successful!')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html')


# Sponsor Registration Page
@app.route('/sponsor-register', methods=['GET', 'POST'])
def sponsor_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        industry = request.form.get('industry')
        budget = request.form.get('budget')

        new_sponsor = Sponsor(username=username, email=email, password=password, company_name=company_name, industry=industry, budget=budget)
        db.session.add(new_sponsor)
        db.session.commit()

        flash('Sponsor registration successful!')
        return redirect(url_for('sponsor_login'))

    return render_template('sponsor_register.html')


# Influencer Registration Page
@app.route('/influencer-register', methods=['GET', 'POST'])
def influencer_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        category = request.form.get('category')
        niche = request.form.get('niche')
        reach = request.form.get('reach')

        new_influencer = Influencer(username=username, email=email, password=password, name=name, category=category, niche=niche, reach=reach)
        db.session.add(new_influencer)
        db.session.commit()

        flash('Influencer registration successful!')
        return redirect(url_for('influencer_login'))

    return render_template('influencer_register.html')



## Now we will defining all the routing for User Login process

# Login first redirects to Role Selection page where the user has to select his role - Admin/Sponsor/Influencer
@app.route('/login')
def login_redirect():
    return render_template('role_selection.html')


# Upon selecting the 'Admin Login' in Role Selection page you are redirected to Admin Login
## I have added a basic security feature of User tracking throughout the App through Session - user.id and role
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username, password=password).first()

        if admin:
            session['user_id'] = admin.id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('admin_login'))

    return render_template('login.html', title='Admin')


# Upon selecting the 'Sponsor Login' in Role Selection page you are redirected to Sponsor Login
## I have added a basic security feature of User tracking throughout the App through Session - user.id and role
@app.route('/sponsor-login', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        sponsor = Sponsor.query.filter_by(username=username, password=password).first()

        if sponsor:
            session['user_id'] = sponsor.id
            session['role'] = 'sponsor'
            return redirect(url_for('sponsor_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('sponsor_login'))

    return render_template('login.html', title='Sponsor')


# Upon selecting the 'Influencer Login' in Role Selection page you are redirected to Influencer Login
## I have added a basic security feature of User tracking throughout the App through Session - user.id and role
@app.route('/influencer-login', methods=['GET', 'POST'])
def influencer_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        influencer = Influencer.query.filter_by(username=username, password=password).first()

        if influencer:
            session['user_id'] = influencer.id
            session['role'] = 'influencer'
            return redirect(url_for('influencer_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('influencer_login'))

    return render_template('login.html', title='Influencer')



## Now we will defining all the routing for Admin Dashboard

# After successful login as Admin, you are redirected to Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'admin':
        sponsors = Sponsor.query.all()
        influencers = Influencer.query.all()
        campaigns = Campaign.query.all()
        return render_template('admin_dashboard.html', sponsors=sponsors, influencers=influencers, campaigns=campaigns)
    else:
        flash('You need to log in as admin to view this page.', 'danger')
        return redirect(url_for('admin_login'))


# This route is to display Sponsors and Influencers for Admin in their Dashboard
@app.route('/admin-users')
def admin_users():
    if 'user_id' in session and session['role'] == 'admin':
        influencers = Influencer.query.all()
        sponsors = Sponsor.query.all()
        return render_template('admin_users.html', influencers=influencers, sponsors=sponsors)
    else:
        flash('You need to log in as admin to view this page.', 'danger')
        return redirect(url_for('admin_login'))


# This route is to flag Sponsors and Influencers through Admin Dashboard
@app.route('/flag-user/<role>/<int:user_id>', methods=['POST'])
def flag_user(role, user_id):
    if 'user_id' in session and session['role'] == 'admin':
        if role == 'sponsor':
            user = Sponsor.query.get(user_id)
        elif role == 'influencer':
            user = Influencer.query.get(user_id)
        else:
            flash('Invalid user role.', 'danger')
            return redirect(url_for('admin_users'))

        if user:
            user.flagged = True
            db.session.commit()
            flash(f'{role.capitalize()} flagged successfully.', 'success')
        else:
            flash('User not found.', 'danger')

        return redirect(url_for('admin_users'))
    else:
        flash('You need to log in as admin to flag users.', 'danger')
        return redirect(url_for('admin_login'))


# This route is to display all Campaigns for Admin in their Dashboard
@app.route('/admin-campaigns')
def admin_campaigns():
    if 'user_id' in session and session['role'] == 'admin':
        campaigns = Campaign.query.all()
        return render_template('admin_campaigns.html', campaigns=campaigns)
    else:
        flash('You need to log in as admin to view this page.', 'danger')
        return redirect(url_for('admin_login'))


# This route is to flag Campaigns through Admin Dashboard
@app.route('/flag-campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    if 'role' in session and session['role'] == 'admin':
        campaign = Campaign.query.get_or_404(campaign_id)
        campaign.flagged = True
        db.session.commit()
        flash(f'Campaign "{campaign.name}" has been flagged.', 'success')
        return redirect(url_for('admin_campaigns'))
    else:
        flash('You need to log in as admin to flag campaigns.', 'danger')
        return redirect(url_for('admin_login'))

  
# This route is to display all Ad-Requests for Admin in their Dashboard
@app.route('/admin-ad-requests')
def admin_ad_requests():
    if 'role' in session and session['role'] == 'admin':
        ad_requests = AdRequest.query.all()
        return render_template('admin_ad_requests.html', ad_requests=ad_requests)
    else:
        flash('You need to log in as admin to view this page.', 'danger')
        return redirect(url_for('admin_login'))


# This route is to flag Ad-Requests through Admin Dashboard
@app.route('/flag-ad-request/<int:ad_request_id>', methods=['POST'])
def flag_ad_request(ad_request_id):
    if 'role' in session and session['role'] == 'admin':
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        ad_request.flagged = True  # Set the flagged attribute to True
        db.session.commit()
        flash(f'Ad Request ID {ad_request_id} has been flagged.', 'success')
        return redirect(url_for('admin_ad_requests'))
    else:
        flash('You need to log in as admin to flag ad requests.', 'danger')
        return redirect(url_for('admin_login'))



## Now we will defining all the routing for Sponsor Dashboard

# After successful login as Sponsor, you are redirected to Sponsor Dashboard
@app.route('/sponsor-dashboard')
def sponsor_dashboard():
    if 'user_id' in session and session['role'] == 'sponsor':
        sponsor_id = session['user_id']
        sponsor = Sponsor.query.get(sponsor_id)
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
        ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor_id).all()
        return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests)
    else:
        flash('You need to log in as sponsor to view this page.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to Create a new Campaign through Sponsor Dashboard
@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if 'user_id' in session and session['role'] == 'sponsor':
        sponsor_id = session['user_id']
        
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            budget = request.form['budget']
            visibility = request.form['visibility']
            category = request.form['category']
            
            # Convert string dates to datetime.date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            new_campaign = Campaign(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                budget=float(budget),
                visibility=visibility,
                category=category,
                sponsor_id=sponsor_id
            )
            db.session.add(new_campaign)
            db.session.commit()
            flash('Campaign created successfully!', 'success')
            return redirect(url_for('sponsor_dashboard'))
        
        return render_template('create_campaign.html')
    
    else:
        flash('You need to log in as a sponsor to create a campaign.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to allow edits in an existing Campaign through Sponsor Dashboard
@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    if 'user_id' in session and session['role'] == 'sponsor':
        campaign = Campaign.query.get_or_404(campaign_id)

        if request.method == 'POST':
            campaign.name = request.form['name']
            campaign.description = request.form['description']
            
            # Convert dates from string to date objects
            campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            
            campaign.budget = float(request.form['budget'])
            campaign.visibility = request.form['visibility']
            campaign.category = request.form['category']
            
            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('sponsor_dashboard'))

        return render_template('edit_campaign.html', campaign=campaign)

    else:
        flash('You need to log in as a sponsor to edit this campaign.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to allow deletion of an existing Campaign through Sponsor Dashboard
@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    if 'user_id' in session and session['role'] == 'sponsor':
        campaign = Campaign.query.get_or_404(campaign_id)
        if campaign.sponsor_id == session['user_id']:
            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully!', 'success')
        else:
            flash('You do not have permission to delete this campaign.', 'danger')
        return redirect(url_for('sponsor_dashboard'))
    else:
        flash('You need to log in as sponsor to delete a campaign.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to Create a new Ad-Request for a specific Campaign through Sponsor Dashboard
## Sponsor even has to assign a particular Influencer for his Ad-Request
@app.route('/create-ad-request/<int:campaign_id>', methods=['GET', 'POST'])
def create_ad_request(campaign_id):
    if 'user_id' in session and session['role'] == 'sponsor':
        if request.method == 'POST':
            influencer_id = request.form['influencer_id']
            messages = request.form['messages']
            requirements = request.form['requirements']
            payment_amount = request.form['payment_amount']
            
            new_ad_request = AdRequest(
                campaign_id=campaign_id,
                influencer_id=influencer_id,
                messages=messages,
                requirements=requirements,
                payment_amount=payment_amount,
                status='Pending'  # Default status
            )
            db.session.add(new_ad_request)
            db.session.commit()
            flash('Ad request created successfully.', 'success')
            return redirect(url_for('sponsor_dashboard'))
        
        campaign = Campaign.query.get_or_404(campaign_id)
        influencers = Influencer.query.all()
        return render_template('create_ad_request.html', campaign=campaign, influencers=influencers)
    else:
        flash('You need to log in as a sponsor to create an ad request.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to Edit an existing Ad-Request for a specific Campaign through Sponsor Dashboard
@app.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def edit_ad_request(ad_request_id):
    if 'user_id' in session and session['role'] == 'sponsor':
        ad_request = AdRequest.query.get_or_404(ad_request_id)

        if request.method == 'POST':
            ad_request.campaign_id = request.form['campaign_id']
            ad_request.influencer_id = request.form['influencer_id']
            ad_request.messages = request.form['messages']
            ad_request.requirements = request.form['requirements']
            ad_request.payment_amount = request.form['payment_amount']
            ad_request.status = request.form['status']

            db.session.commit()
            flash('Ad request updated successfully!', 'success')
            return redirect(url_for('sponsor_dashboard'))

        campaigns = Campaign.query.filter_by(sponsor_id=session['user_id']).all()
        influencers = Influencer.query.all()  # Assuming you have an Influencer model

        return render_template('edit_ad_request.html', ad_request=ad_request, campaigns=campaigns, influencers=influencers)

    else:
        flash('You need to log in as sponsor to edit this ad request.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to allow deletion of an existing Ad-Request through Sponsor Dashboard
@app.route('/delete-ad-request/<int:ad_request_id>', methods=['POST'])
def delete_ad_request(ad_request_id):
    if 'user_id' in session and session['role'] == 'sponsor':
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        db.session.delete(ad_request)
        db.session.commit()
        flash('Ad request deleted successfully.', 'success')
        return redirect(url_for('sponsor_dashboard'))
    else:
        flash('You need to log in as sponsor to delete an ad request.', 'danger')
        return redirect(url_for('sponsor_login'))


# This route is to view the logged in Sponsor's registered profile
@app.route('/sponsor-profile')
def sponsor_profile():
    sponsor_id = session.get('user_id')
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        flash('Sponsor not found!', 'danger')
        return redirect(url_for('sponsor_dashboard'))
    return render_template('sponsor_profile.html', sponsor=sponsor)


# This route allows the logged in Sponsor to edit their profile
@app.route('/edit-sponsor-profile', methods=['GET', 'POST'])
def edit_sponsor_profile():
    sponsor_id = session.get('user_id')
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        flash('Sponsor not found!', 'danger')
        return redirect(url_for('sponsor_dashboard'))

    if request.method == 'POST':
        sponsor.username = request.form['username']
        sponsor.email = request.form['email']
        sponsor.password = request.form['password']
        sponsor.company_name = request.form['company_name']
        sponsor.industry = request.form['industry']
        sponsor.budget = float(request.form['budget'])
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('sponsor_profile'))

    return render_template('edit_sponsor_profile.html', sponsor=sponsor)


# This route handles the Negotiation at Sponsor end
@app.route('/handle_negotiation/<int:ad_request_id>', methods=['POST'])
def handle_negotiation(ad_request_id):
    if 'user_id' in session and session['role'] == 'sponsor':
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        action = request.form['action']
        if action == 'accept':
            ad_request.status = 'Accepted'
            flash('Negotiation accepted!', 'success')
        elif action == 'reject':
            ad_request.status = 'Rejected'
            flash('Negotiation rejected!', 'danger')
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))
    else:
        flash('You need to log in as sponsor to view this page.', 'danger')
        return redirect(url_for('sponsor_login'))
    


## Now we will defining all the routing for Influencer Dashboard

# After successful login as Influencer, you are redirected to Influencer Dashboard
@app.route('/influencer-dashboard')
def influencer_dashboard():
    if 'user_id' in session and session['role'] == 'influencer':
        influencer_id = session['user_id']
        influencer = Influencer.query.get(influencer_id)
        ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
        return render_template('influencer_dashboard.html', influencer=influencer, ad_requests=ad_requests)
    else:
        flash('You need to log in as influencer to view this page.', 'danger')
        return redirect(url_for('influencer_login'))


# This route is to display all existing Campaigns through Influencer Dashboard
## Influencer can filter them according to Category or Budget
@app.route('/influencer/campaigns', methods=['GET', 'POST'])
def view_campaigns():
    category = request.args.get('category')
    budget = request.args.get('budget')

    campaigns = Campaign.query.filter(
        Campaign.visibility == 'public',
        or_(
            Campaign.category.ilike(f'%{category}%') if category else True,
            Campaign.budget <= float(budget) if budget else True
        )
    ).all()

    return render_template('view_campaigns.html', campaigns=campaigns)


# This route is to Accept/Reject an Ad-Request from Sponsor through Influencer Dashboard
@app.route('/ad-request-action/<int:ad_request_id>', methods=['POST'])
def ad_request_action(ad_request_id):
    if 'user_id' in session and session['role'] == 'influencer':
        action = request.form.get('action')
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        if action == 'accept':
            ad_request.status = 'Accepted'
        elif action == 'reject':
            ad_request.status = 'Rejected'
        db.session.commit()
        flash(f'Ad request {action}ed successfully.', 'success')
        return redirect(url_for('influencer_dashboard'))
    else:
        flash('You need to log in as an influencer to perform this action.', 'danger')
        return redirect(url_for('influencer_login'))


# This route is to view the logged in Influencer's registered profile
@app.route('/influencer-profile')
def influencer_profile():
    influencer_id = session.get('user_id')
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash('Influencer not found!', 'danger')
        return redirect(url_for('influencer_dashboard'))
    return render_template('influencer_profile.html', influencer=influencer)


# This route allows the logged in Influencer to edit their profile
@app.route('/edit-influencer-profile', methods=['GET', 'POST'])
def edit_influencer_profile():
    influencer_id = session.get('user_id')
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash('Influencer not found!', 'danger')
        return redirect(url_for('influencer_dashboard'))

    if request.method == 'POST':
        influencer.username = request.form['username']
        influencer.email = request.form['email']
        influencer.password = request.form['password']
        influencer.name = request.form['name']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = int(request.form['reach'])
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('influencer_profile'))

    return render_template('edit_influencer_profile.html', influencer=influencer)


# This route handles the Negotiation at Influencer end
@app.route('/negotiate_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def negotiate_ad_request(ad_request_id):
    if 'user_id' in session and session['role'] == 'influencer':
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        if request.method == 'POST':
            negotiation_terms = request.form['negotiation_terms']
            ad_request.negotiation_terms = negotiation_terms
            ad_request.status = 'Negotiation'
            db.session.commit()
            flash('Negotiation terms sent!', 'success')
            return redirect(url_for('influencer_dashboard'))
        return render_template('negotiate_ad_request.html', ad_request=ad_request)
    else:
        flash('You need to log in as influencer to view this page.', 'danger')
        return redirect(url_for('influencer_login'))


# This route handles the submission of Negotiation terms at Influencer end
@app.route('/submit_negotiation/<int:ad_request_id>', methods=['POST'])
def submit_negotiation(ad_request_id):
    if 'user_id' in session and session['role'] == 'influencer':
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        negotiation_terms = request.form['negotiation_terms']
        ad_request.negotiation_terms = negotiation_terms
        ad_request.status = 'Negotiation'
        db.session.commit()
        flash('Negotiation terms sent!', 'success')
        return redirect(url_for('influencer_dashboard'))
    else:
        flash('You need to log in as influencer to view this page.', 'danger')
        return redirect(url_for('influencer_login'))


# This route handles the display of specific Ad-Request details in Sponsor and Influencer Dashboards
@app.route('/view_ad_request/<int:ad_request_id>')
def view_ad_request(ad_request_id):
    if 'user_id' in session:
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        return render_template('view_ad_request.html', ad_request=ad_request)
    else:
        flash('You need to log in to view this page.', 'danger')
        return redirect(url_for('login'))


# This is the Logout button routing for the whole app
## During the logout process as a basic security feature of it pops out user.id and role from Session
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # To create all tables defined in models.py
    app.run(debug=True)