import profile
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask_mongoengine import MongoEngine
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import os
import json
from enum import Enum
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = '3f4ceff196960c4decbc7a5b26cfac18'

app.config['MONGO_DBNAME'] = 'medical_records'
# localhost to be replaced by mongo_container in below line for production
app.config['MONGO_URI'] = 'mongodb://localhost:27017/medical_records'

CORS(app)

mongo = PyMongo(app)

# localhost to be replaced by mongo_container in below line for production
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/medical_records'
}
db = MongoEngine(app)
print(db)


class StaffInfo(db.Document):
    firstName = db.StringField()
    secondName = db.StringField()
    mobileNo = db.StringField()
    emailId = db.StringField()
    pswd = db.StringField()


# class DevicePrevUser(db.EmbeddedDocument):
#     userId = db.StringField()
#     assignedOn = db.DateTimeField()
#     returnedOn = db.DateTimeField()

# class DeviceRegistration(db.Document):
#     deviceName = db.StringField()
#     deviceVersion = db.StringField()
#     deviceFirmwareVersion = db.StringField()
#     firmwareUpdatedOn = db.DateTimeField()
#     macAddress = db.StringField()
#     currentUserId = db.StringField()
#     assignedOn = db.DateTimeField()
#     previouUsers = db.EmbeddedDocumentListField(DevicePrevUser)


class CommunicationChannel(Enum):
    Both = 1
    OnlyMobile = 2
    OnlyBLEGateway = 3


class SamplingRateInfo(db.EmbeddedDocument):
    heartRate = db.IntField()
    spo2 = db.IntField()
    temperature = db.IntField()
    activity = db.IntField()


class DeviceInfo(db.Document):
    deviceId = db.StringField()
    communicationChannel = db.IntField()
    samplingRateInfo = db.EmbeddedDocumentField(SamplingRateInfo)
    readingsPerDay = db.IntField()
    monitoringSchedule = db.ListField(db.DateTimeField())


class Record(db.EmbeddedDocument):
    creationDT = db.StringField()
    fullDT = db.StringField()
    recordName = db.StringField()


class EmergencyContact(db.EmbeddedDocument):
    firstName = db.StringField()
    secondName = db.StringField()
    mobileNo = db.StringField()
    emailId = db.StringField()


class UserRegistration(db.Document):
    firstName = db.StringField()
    secondName = db.StringField()
    DOB = db.DateTimeField(default=datetime.datetime.utcnow)
    mobileNo = db.StringField()
    emergencyContact = db.EmbeddedDocumentField(EmergencyContact)
    emailId = db.StringField()
    gender = db.StringField()
    password = db.StringField()
    caregiverId = db.StringField()
    deviceId = db.StringField()
    activeUser = db.BooleanField()
    validEmail = db.BooleanField()
    recordList = db.EmbeddedDocumentListField(Record)


class DeviceData(db.Document):
    timestamps = db.StringField()
    sample_Nos = db.IntField()
    ledc1_pd1s = db.StringField()
    ledc1_pd2s = db.StringField()
    ledc2_pd1s = db.StringField()
    ledc2_pd2s = db.StringField()
    ledc3_pd1s = db.StringField()
    ledc3_pd2s = db.StringField()
    accxs = db.IntField()
    accys = db.IntField()
    acczs = db.IntField()
    temperatures = db.IntField()
    hrs = db.IntField()
    rrs = db.IntField()
    activity_classs = db.IntField()
    scd_states = db.IntField()
    spo2s = db.IntField()
    starts = db.IntField()


def parseDate(obj, key):
    strdate = obj[key]
    datevalue = datetime.datetime.strptime(strdate, "%Y-%m-%d")
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
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print("asdf", data)
            current_user = UserRegistration.objects(
                emailId=data['emailId'])
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator


'''
end of jwt
'''


@app.route('/userRegistration', methods=['POST'])
def add_record():
    '''
    read the contents of json and dump in mongo
    '''
    requested_data = request.get_json()
    requested_data = parseDate(requested_data, "DOB")
    requested_data = hashPassword(requested_data, "password")
    res = UserRegistration.objects(emailId=requested_data["emailId"])
    print(res)
    if len(res) == 0:
        added_user = UserRegistration(**requested_data).save()
        return jsonify({'result': "added-successfully", "id": str(added_user.id)})
    else:
        return ({'result': "user already exist"})


@app.route('/login', methods=['POST'])
def login():
    print("start login")
    auth = request.get_json()
    # print("auth = "+str(auth.username))
    # uname = request.args.get("username")
    print((auth))  # "uname " + string ["userName"])
    # here username to cont
    # ain the email id as that is the primary key

    if not auth or not auth["userName"] or not auth["password"]:
        return ({'could not verify', 401, {'Authentication': 'login required"'}})

    # .query.filter_by(emailId=auth.username).first()
    user = UserRegistration.objects(emailId=auth["userName"])
    print(len(user))
    print("here we go  " + str(user[0].password))  # .password))
    print("token encode "+user[0].emailId)
    if check_password_hash(user[0].password, auth["password"]):
        token = jwt.encode({'emailId': user[0].emailId, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")

        return jsonify({'token': token, 'emailId': user[0].emailId})

    return ({'could not verify',  401, {'Authentication': '"login required"'}})


@app.route('/users', methods=['GET'])
@token_required
def get_all_users(u=None):
    print("request is here")
    users = UserRegistration.objects()
    result = []
    for user in users:
        user_data = {}
        user_data['secondName'] = user.secondName
        user_data['firstName'] = user.firstName
        user_data['password'] = user.password
        user_data['emailId'] = user.emailId

        result.append(user_data)
    return jsonify({'users': result})


@app.route('/updateCaregiverDetails', methods=['POST'])
def updateCaregiverDetails():
    try:
        requested_data = request.get_json()
        userid = request.args.get("userId")
        users = UserRegistration.objects(id=ObjectId(userid))
        if(len(users) > 0):
            user = users.first()
            staffcursor = StaffInfo.objects(emailId=requested_data["emailId"])
            if (staffcursor.count() == 0):
                newStaff = StaffInfo(**requested_data).save()
                setattr(user, "caregiverId", str(newStaff.id))
            else:
                setattr(user, "caregiverId", str(staffcursor.first().id))
            user.save()
            return ({'result': "successfully updated"})
        else:
            return ({'result': "user doesnot exist"})
    except:
        return ({'result': "unsuccessfully operation"})


@app.route('/updateEmergencyContact', methods=['POST'])
def updateEmergencyContact():
    try:
        requested_data = request.get_json()
        userid = request.args.get("userId")
        users = UserRegistration.objects(id=ObjectId(userid))
        if(len(users) > 0):
            user = users.first()
            print(user)
            emergencyContact = EmergencyContact(**requested_data)
            setattr(user, "emergencyContact", emergencyContact)
            user.save()
            return ({'result': "successfully updated"})
        else:
            return ({'result': "user doesnot exist"})
    except:
        return ({'result': "unsuccessfully operation"})


@app.route('/updateUserProfile', methods=['POST'])
def updateUserProfile():
    try:
        requested_data = request.get_json()
        requested_data = parseDate(requested_data, "DOB")
        userid = request.args.get("userId")
        print("userid = ", userid)
        users = UserRegistration.objects(id=ObjectId(userid))
        if(len(users) > 0):
            user = users.first()
            print(user)
            setattr(user, "firstName", requested_data["firstName"])
            setattr(user, "secondName", requested_data["secondName"])
            setattr(user, "mobileNo", requested_data["mobileNo"])
            setattr(user, "DOB", requested_data["DOB"])
            setattr(user, "password", requested_data["password"])
            user.save()
            return ({'result': "successfully updated"})
        else:
            return ({'result': "user doesnot exist"})
    except:
        return ({'result': "unsuccessfully operation"})


@app.route('/updateMonitoringSchedule', methods=['POST'])
def updateMonitoringSchedule():
    requested_data = request.get_json()
    requested_data = parseMonitoringSchedule(
        requested_data, "monitoringSchedule")
    deviceId = request.args.get("deviceId")
    devices = DeviceInfo.objects(deviceId=deviceId)
    if(len(devices) > 0):
        device = devices.first()
    else:
        device = DeviceInfo()
        setattr(device, "deviceId", deviceId)
        setattr(device, "communicationChannel", 1)
        samplingRateInfo = SamplingRateInfo()
        setattr(samplingRateInfo, "heartRate", 256)
        setattr(samplingRateInfo, "spo2", 256)
        setattr(samplingRateInfo, "temperature", 256)
        setattr(samplingRateInfo, "activity", 256)
        setattr(device, "samplingRateInfo", samplingRateInfo)

    setattr(device, "readingsPerDay", requested_data["readingsPerDay"])
    device["monitoringSchedule"] = requested_data["monitoringSchedule"]
    device = device.save()
    return {"result": "updated successfully"}


@app.route('/updateSamplingRateSettings', methods=['POST'])
def updateSamplingRateSettings():
    requested_data = request.get_json()
    deviceId = request.args.get("deviceId")
    devices = DeviceInfo.objects(deviceId=deviceId)
    if(len(devices) > 0):
        device = devices.first()
    else:
        device = DeviceInfo()
        setattr(device, "deviceId", deviceId)
        setattr(device, "readingsPerDay", 0)
        device["monitoringSchedule"] = []

    setattr(device, "communicationChannel",
            requested_data["communicationChannel"])
    samplingRateInfo = SamplingRateInfo(**requested_data["samplingRateInfo"])
    setattr(device, "samplingRateInfo", samplingRateInfo)
    device = device.save()
    return {"result": "updated successfully"}


@app.route('/hello', methods=['POST'])
def hello():
    requested_data = request.get_json()
    print('requested_data', requested_data)
    return {"result": "updated successfully"}, 200


@app.route('/file', methods=['GET', 'POST'])
def index():
    upload_form = """<h1>Save file</h1>
                     <form method="POST" enctype="multipart/form-data">
                     <input type="file" name="file" id="file">
                     <br><br>
                     <input type="submit">
                     </form>"""

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            file_data = json.load(file)
            userid = file_data['userid']
            print("user id "+userid)
            usersdata = UserRegistration.objects(id=ObjectId(userid))
            if(len(usersdata) > 0):
                print("we are here")
                user = usersdata.first()
                print(user.emailId)
                recordLst = user.recordList
                print(len(recordLst))
                # ll = recordList.last()
                print(recordLst)
                # get date
                datenow = datetime.datetime.utcnow()
                # print(ll.recordName)
                # there are 3 cases, if the recordlist len = 0 then create new collection
                # if recordlist len > 0 then find the latest table and check for number of records
                # if they are less than 15K then just add on to that collections.
                # if they are > 15k then close the latest and create new.
                if(len(recordLst) == 0):

                    # geenrate new table name
                    newcollname = user.emailId+"_" + \
                        datenow.strftime("%Y_%m_%d_%H_%M_%S")
                    print("new collection name"+newcollname)
                    # create new collection and push data from file to new collection.
                    db.get_db()[newcollname].insert_many(file_data['data'])
                    # update the user collections
                    temprecordLst = Record()
                    setattr(temprecordLst, "creationDT",
                            datenow.strftime("%Y %m %d"))
                    setattr(temprecordLst, "fullDT", "0")
                    setattr(temprecordLst, "recordName", newcollname)
                    setattr(user, "recordList", [temprecordLst])
                    # print("tempreclst is set now", temprecordLst)
                    user.save()
                    print("updated the record")
                else:
                    print("already has records")
                    currColl = ""

                    for reclst in recordLst:
                        if(reclst['fullDT'] == "0"):
                            currColl = reclst['recordName']
                            currRec = reclst

                    print("currecnt coll is ", currColl)
                    print("total records", db.get_db()
                          [currColl].find().count())
                    if db.get_db()[currColl].find().count() < 6:
                        print("less than 15K")
                        db.get_db()[currColl].insert_many(file_data['data'])
                    else:
                        print("greater than 15K")
                        currRec['fullDT'] = datenow.strftime("%Y %m %d")

                        temprecordLst = Record()

                        newcollname = user.emailId+"_" + \
                            datenow.strftime("%Y_%m_%d_%H_%M_%S")

                        setattr(temprecordLst, "creationDT",
                                datenow.strftime("%Y %m %d"))
                        setattr(temprecordLst, "fullDT", "0")
                        setattr(temprecordLst, "recordName", newcollname)
                        recordLst.append(temprecordLst)
                        #setattr(user, "recordList", [temprecordLst])
                        # print("tempreclst is set now", temprecordLst)

                        print("new collection name"+newcollname)
                        # create new collection and push data from file to new collection.
                        db.get_db()[newcollname].insert_many(file_data['data'])

                        user.save()

                    '''
                    instead of doing this, directly check from the user -> recordlst whose full DT = 0
                    collist = db.get_db().list_collection_names()
                    print(collist)
                    userCollLst = []
                    for coll_name in db.get_db().list_collection_names():
                        print("collection:{}".format(coll_name))
                        if user.emailId in coll_name:
                            userCollLst.append(coll_name)
                    print(userCollLst)
                    userCollLst.sort()
                    print("final sorted list", userCollLst)
                    # print(usersdata)
                    '''

            mongo.save_file(file.filename, file)
            return {"file name": file.filename}
    return upload_form
    return


@ app.route('/create', methods=['POST'])
def create():
    if 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        mongo.save_file(profile_image.filename, profile_image)
        mongo.db.users.insert({'username': request.form.get(
            'username'), 'profile_image_name': profile_image.filename})
    return 'Done !'


@ app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


''' below code not required'''
# @app.route('/profile/<username>')
# def profile(username):
# user = mongo.db.users.find_one_or_404({'username': username})
# return f'''
# <h1>{username}</h1>
# <img src="{url_for('file',filename=user['profile_image_name'])}">
# '''


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
