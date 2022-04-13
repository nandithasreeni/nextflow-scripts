from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from enum import Enum
import datetime

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

# this is required to udpate the dash board and receive data from the device.


class SummaryRecordedData(db.EmbeddedDocument):
    temperature = db.StringField()
    hr = db.StringField()
    spo2 = db.StringField()
    batterycharge = db.StringField()
    sleephrs = db.StringField()
    numberofsteps = db.StringField()
    lastupdated = db.DateTimeField()


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
    summaryData = db.EmbeddedDocumentField(SummaryRecordedData)


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
