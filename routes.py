from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from models import db, Admin, Opportunity

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    full_name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not full_name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
        
    if Admin.query.filter_by(email=email).first():
        return jsonify({"error": "Account already exists"}), 400
        
    hashed_pw = generate_password_hash(password, method='scrypt')
    new_admin = Admin(full_name=full_name, email=email, password_hash=hashed_pw)
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({"success": True}), 201

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)
    
    user = Admin.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
        
    login_user(user, remember=remember)
    return jsonify({"success": True}), 200

@api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True}), 200

@api_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = Admin.query.filter_by(email=email).first()
    
    if user:
        reset_token = uuid.uuid4().hex
        print(f"PASSWORD RESET LINK FOR {email}: /reset-password?token={reset_token}")
        
    return jsonify({"success": True}), 200

@api_bp.route('/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()
    output = []
    for op in ops:
        output.append({
            'id': op.id,
            'title': op.title,
            'duration': op.duration,
            'start_date': op.start_date,
            'description': op.description,
            'skills': op.skills,
            'category': op.category,
            'future_opportunities': op.future_opportunities,
            'max_applicants': op.max_applicants
        })
    return jsonify({"status": "success", "data": output}), 200

@api_bp.route('/opportunities', methods=['POST'])
@login_required
def add_opportunity():
    data = request.get_json()
    
    required_fields = ['title', 'duration', 'start_date', 'description', 'skills', 'category', 'future_opportunities']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
            
    max_applicants = data.get('max_applicants')
    if max_applicants:
        try:
            max_applicants = int(max_applicants)
        except ValueError:
            max_applicants = None
            
    new_op = Opportunity(
        title=data['title'],
        duration=data['duration'],
        start_date=data['start_date'],
        description=data['description'],
        skills=data['skills'],
        category=data['category'],
        future_opportunities=data['future_opportunities'],
        max_applicants=max_applicants,
        admin_id=current_user.id
    )
    
    db.session.add(new_op)
    db.session.commit()
    
    return jsonify({"status": "success", "data": {"id": new_op.id}}), 201

@api_bp.route('/opportunities/<int:id>', methods=['GET'])
@login_required
def get_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({"error": "Not found"}), 404
        
    return jsonify({
        "status": "success", 
        "data": {
            'id': op.id,
            'title': op.title,
            'duration': op.duration,
            'start_date': op.start_date,
            'description': op.description,
            'skills': op.skills,
            'category': op.category,
            'future_opportunities': op.future_opportunities,
            'max_applicants': op.max_applicants
        }
    }), 200

@api_bp.route('/opportunities/<int:id>', methods=['PUT'])
@login_required
def edit_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({"error": "Not found"}), 404
        
    data = request.get_json()
    required_fields = ['title', 'duration', 'start_date', 'description', 'skills', 'category', 'future_opportunities']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
            
    op.title = data['title']
    op.duration = data['duration']
    op.start_date = data['start_date']
    op.description = data['description']
    op.skills = data['skills']
    op.category = data['category']
    op.future_opportunities = data['future_opportunities']
    
    max_applicants = data.get('max_applicants')
    if max_applicants:
        try:
            max_applicants = int(max_applicants)
        except ValueError:
            max_applicants = None
    op.max_applicants = max_applicants
            
    db.session.commit()
    return jsonify({"status": "success"}), 200

@api_bp.route('/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_opportunity(id):
    op = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first()
    if not op:
        return jsonify({"error": "Not found"}), 404
        
    db.session.delete(op)
    db.session.commit()
    return jsonify({"status": "success"}), 200
