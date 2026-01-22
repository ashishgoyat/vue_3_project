from functools import wraps
from flask import jsonify
from flask_security import current_user

def active_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'message': 'Authentication required'}), 401
        if not getattr(current_user, 'active', True):
            return jsonify({'message': 'User account is inactive'}), 403
        return f(*args, **kwargs)
    return wrapper

def roles_list(roles):
    role_list = []
    for role in roles:
        role_list.append(role.name)
    return role_list