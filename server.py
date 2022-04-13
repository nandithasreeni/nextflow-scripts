import profile
import baseStructure
import commonFunctions
from bson.json_util import dumps
from bson.objectid import ObjectId
import time
import datetime
import os
import json
from flask import request
from flask import jsonify


@baseStructure.app.route('/userRegistration', methods=['POST'])
def add_record():
    '''
    read the contents of json and dump in mongo
    '''
    requested_data = request.get_json()
    requested_data = commonFunctions.parseDate(requested_data, "DOB")
    requested_data = commonFunctions.hashPassword(requested_data, "password")
    res = baseStructure.UserRegistration.objects(
        emailId=requested_data["emailId"])
    print(res)
    if len(res) == 0:
        summaryObj = baseStructure.SummaryRecordedData()
        setattr(summaryObj, "temperature", "0")
        setattr(summaryObj, "hr", "0")
        setattr(summaryObj, "spo2", "0")
        setattr(summaryObj, "batterycharge", "0")
        setattr(summaryObj, "sleephrs", "0")
        setattr(summaryObj, "numberofsteps", "0")
        setattr(summaryObj, "lastupdated",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # commonFunctions.parseDateTime(summaryObj, "lastupdated")
        # print(str(requested_data))

        added_user = baseStructure.UserRegistration(**requested_data)
        added_user.summaryData = summaryObj
        added_user.save()
        return jsonify({'result': "added-successfully", "id": str(added_user.id)})
    else:
        return ({'result': "user already exist"})


@baseStructure.app.route('/login', methods=['POST'])
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
    user = baseStructure.UserRegistration.objects(emailId=auth["userName"])
    print(len(user))
    print("here we go  " + str(user[0].password))  # .password))
    print("token encode "+user[0].emailId)
    if commonFunctions.check_password_hash(user[0].password, auth["password"]):
        token = commonFunctions.jwt.encode({'emailId': user[0].emailId, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=45)}, baseStructure.app.config['SECRET_KEY'], "HS256")

        return jsonify({'token': token, 'emailId': user[0].emailId})

    return ({'could not verify',  401, {'Authentication': '"login required"'}})


@baseStructure.app.route('/users', methods=['GET'])
@commonFunctions.token_required
def get_all_users(u=None):
    print("request is here")
    users = baseStructure.UserRegistration.objects()
    result = []
    for user in users:
        user_data = {}
        user_data['secondName'] = user.secondName
        user_data['firstName'] = user.firstName
        user_data['password'] = user.password
        user_data['emailId'] = user.emailId

        result.append(user_data)
    return jsonify({'users': result})


@baseStructure.app.route('/updateCaregiverDetails', methods=['POST'])
def updateCaregiverDetails():
    try:
        requested_data = request.get_json()
        userid = request.args.get("userId")
        users = baseStructure.UserRegistration.objects(id=ObjectId(userid))
        if(len(users) > 0):
            user = users.first()
            staffcursor = baseStructure.StaffInfo.objects(
                emailId=requested_data["emailId"])
            if (staffcursor.count() == 0):
                newStaff = baseStructure.StaffInfo(**requested_data).save()
                setattr(user, "caregiverId", str(newStaff.id))
            else:
                setattr(user, "caregiverId", str(staffcursor.first().id))
            user.save()
            return ({'result': "successfully updated"})
        else:
            return ({'result': "user doesnot exist"})
    except:
        return ({'result': "unsuccessfully operation"})


@baseStructure.app.route('/updateEmergencyContact', methods=['POST'])
def updateEmergencyContact():
    try:
        requested_data = request.get_json()
        userid = request.args.get("userId")
        users = baseStructure.UserRegistration.objects(id=ObjectId(userid))
        if(len(users) > 0):
            user = users.first()
            print(user)
            emergencyContact = baseStructure.EmergencyContact(**requested_data)
            setattr(user, "emergencyContact", emergencyContact)
            user.save()
            return ({'result': "successfully updated"})
        else:
            return ({'result': "user doesnot exist"})
    except:
        return ({'result': "unsuccessfully operation"})


@baseStructure.app.route('/updateUserProfile', methods=['POST'])
def updateUserProfile():
    try:
        requested_data = request.get_json()
        requested_data = commonFunctions.parseDate(requested_data, "DOB")
        userid = request.args.get("userId")
        print("userid = ", userid)
        users = baseStructure.UserRegistration.objects(id=ObjectId(userid))
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


@baseStructure.app.route('/updateUserSampleReadings', methods=['POST'])
def updateUserSampleReadings():
    try:
        print("data reached here")
        requested_data = request.get_json()
        userid = request.args.get("userId")
        users = baseStructure.UserRegistration.objects(id=ObjectId(userid))
        if(len(users) > 0):
            user = users.first()
            summaryData = user["summaryData"]
            print(requested_data)
            summaryData.temperature = requested_data["Temperature"]
            summaryData.hr = requested_data["HR"]
            summaryData.spo2 = requested_data["SPO2"]
            summaryData.batterycharge = requested_data["BatteryCharge"]
            summaryData.sleephrs = requested_data["Sleep"]
            summaryData.numberofsteps = requested_data["Footsteps"]
            # print("summary data date 1", datetime.datetime.strptime(
            #    requested_data["Lastupdate"], "%d-%m-%Y %H:%M:%S"))

            summaryData.lastupdated = datetime.datetime.strptime(
                requested_data["Lastupdate"], "%d-%m-%Y %H:%M:%S")
            #print("summary data date 2", summaryData.lastupdated)

            # setattr(user, "firstName", requested_data["firstName"])

            # user["summaryData"] = summaryData
            user.save()
            return ({'result': "succeessfully updated"})
    except:
        return ({'result': "unsuccessfully operation"})


@baseStructure.app.route('/updateMonitoringSchedule', methods=['POST'])
def updateMonitoringSchedule():
    requested_data = request.get_json()
    requested_data = commonFunctions.parseMonitoringSchedule(
        requested_data, "monitoringSchedule")
    deviceId = request.args.get("deviceId")
    devices = baseStructure.DeviceInfo.objects(deviceId=deviceId)
    if(len(devices) > 0):
        device = devices.first()
    else:
        device = baseStructure.DeviceInfo()
        setattr(device, "deviceId", deviceId)
        setattr(device, "communicationChannel", 1)
        samplingRateInfo = baseStructure.SamplingRateInfo()
        setattr(samplingRateInfo, "heartRate", 256)
        setattr(samplingRateInfo, "spo2", 256)
        setattr(samplingRateInfo, "temperature", 256)
        setattr(samplingRateInfo, "activity", 256)
        setattr(device, "samplingRateInfo", samplingRateInfo)

    setattr(device, "readingsPerDay", requested_data["readingsPerDay"])
    device["monitoringSchedule"] = requested_data["monitoringSchedule"]
    device = device.save()
    return {"result": "updated successfully"}


@baseStructure.app.route('/updateSamplingRateSettings', methods=['POST'])
def updateSamplingRateSettings():
    requested_data = request.get_json()
    deviceId = request.args.get("deviceId")
    devices = baseStructure.DeviceInfo.objects(deviceId=deviceId)
    if(len(devices) > 0):
        device = devices.first()
    else:
        device = baseStructure.DeviceInfo()
        setattr(device, "deviceId", deviceId)
        setattr(device, "readingsPerDay", 0)
        device["monitoringSchedule"] = []

    setattr(device, "communicationChannel",
            requested_data["communicationChannel"])
    samplingRateInfo = baseStructure.SamplingRateInfo(
        **requested_data["samplingRateInfo"])
    setattr(device, "samplingRateInfo", samplingRateInfo)
    device = device.save()
    return {"result": "updated successfully"}


@baseStructure.app.route('/hello', methods=['POST'])
def hello():
    requested_data = request.get_json()
    print('requested_data', requested_data)
    return {"result": "updated successfully"}, 200


@baseStructure.app.route('/file', methods=['GET', 'POST'])
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
            usersdata = baseStructure.UserRegistration.objects(
                id=ObjectId(userid))
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
                    baseStructure.db.get_db()[newcollname].insert_many(
                        file_data['data'])
                    # update the user collections
                    temprecordLst = baseStructure.Record()
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
                    print("total records", baseStructure.db.get_db()
                          [currColl].find().count())
                    if baseStructure.db.get_db()[currColl].find().count() < 6:
                        print("less than 15K")
                        baseStructure.db.get_db()[currColl].insert_many(
                            file_data['data'])
                    else:
                        print("greater than 15K")
                        currRec['fullDT'] = datenow.strftime("%Y %m %d")

                        temprecordLst = baseStructure.Record()

                        newcollname = user.emailId+"_" + \
                            datenow.strftime("%Y_%m_%d_%H_%M_%S")

                        setattr(temprecordLst, "creationDT",
                                datenow.strftime("%Y %m %d"))
                        setattr(temprecordLst, "fullDT", "0")
                        setattr(temprecordLst, "recordName", newcollname)
                        recordLst.append(temprecordLst)
                        # setattr(user, "recordList", [temprecordLst])
                        # print("tempreclst is set now", temprecordLst)

                        print("new collection name"+newcollname)
                        # create new collection and push data from file to new collection.
                        baseStructure.db.get_db()[newcollname].insert_many(
                            file_data['data'])

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

            baseStructure.mongo.save_file(file.filename, file)
            return {"file name": file.filename}
    return upload_form
    return


@baseStructure.app.route('/create', methods=['POST'])
def create():
    if 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        baseStructure.mongo.save_file(profile_image.filename, profile_image)
        baseStructure.mongo.db.users.insert({'username': request.form.get(
            'username'), 'profile_image_name': profile_image.filename})
    return 'Done !'


@baseStructure.app.route('/file/<filename>')
def file(filename):
    return baseStructure.mongo.send_file(filename)


''' below code not required'''
# @app.route('/profile/<username>')
# def profile(username):
# user = mongo.db.users.find_one_or_404({'username': username})
# return f'''
# <h1>{username}</h1>
# <img src="{url_for('file',filename=user['profile_image_name'])}">
# '''


if __name__ == '__main__':
    baseStructure.app.run(host="0.0.0.0", debug=True, port=5000)
