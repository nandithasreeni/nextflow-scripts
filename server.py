from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask_mongoengine import MongoEngine
import datetime
import os
import json
from enum import Enum
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'medical_records'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/medical_records'

mongo = PyMongo(app)

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


def parseDate(obj, key):
    strdate = obj[key]
    datevalue = datetime.datetime.strptime(strdate, "%Y-%m-%d")
    #datevalue = datetime.datetime.strptime(strdate, "MM/dd/yyyy")
    obj[key] = datevalue
    return obj


def parseMonitoringSchedule(obj, key):
    formatedTime = []
    for item in obj[key]:
        strdate = item
        datevalue = datetime.datetime.strptime(strdate, "%H:%M:%S")
        formatedTime.append(datevalue)
    obj[key] = formatedTime
    return obj


@app.route('/userRegistration', methods=['POST'])
def add_record():
    '''
    read the contents of json and dump in mongo
    '''
    requested_data = request.get_json()
    requested_data = parseDate(requested_data, "DOB")
    res = UserRegistration.objects(emailId=requested_data["emailId"])
    print(res)
    if len(res) == 0:
        added_user = UserRegistration(**requested_data).save()
        return jsonify({'result': "added-successfully", "id": str(added_user.id)})
    else:
        return ({'result': "user already exist"})


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


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
