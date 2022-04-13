from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask import request
import jwt
from flask import jsonify
import baseStructure


def parseDate(obj, key):
    strdate = obj[key]
    datevalue = datetime.datetime.strptime(strdate, "%Y-%m-%d")
    # datevalue = datetime.datetime.strptime(strdate, "MM/dd/yyyy")
    obj[key] = datevalue
    return obj


def parseDateTime(obj, key):
    strdate = str(obj[key])
    datevalue = datetime.datetime.strptime(strdate, "%Y-%m-%d %H-%M-%S")
    # datevalue = datetime.datetime.strptime(strdate, "MM/dd/yyyy")
    obj[key] = datevalue
    return obj


def hashPassword(obj, key):
    obj[key] = generate_password_hash(obj[key], method='sha256')
    return obj


def parseMonitoringSchedule(obj, key):
    formatedTime = []
    for item in obj[key]:
        strdate = item
        datevalue = datetime.datetime.strptime(strdate, "%H:%M:%S")
        formatedTime.append(datevalue)
    obj[key] = formatedTime
    return obj


'''
for jwt
'''


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        print(request.headers['Authorization'])
        # 'x-access-tokens' in request.headers:
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']  # ['x-access-tokens']
        print(token.split(" ")[1])
        token = token.split(" ")[1]
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(
                token, baseStructure.app.config['SECRET_KEY'], algorithms=["HS256"])
            print("asdf", data)
            current_user = baseStructure.UserRegistration.objects(
                emailId=data['emailId'])
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


'''
end of jwt
'''
