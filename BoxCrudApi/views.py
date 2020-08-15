from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta
from .models import Box
from .serializers import BoxSerializers
import json

A1 = 100
V1 = 1000
L1 = 100
L2 = 50

#Helper function for creating the response so we eleminate duplication of code
def createResponse(status, message, data=None):
    response = {'status': status,
                'message': message}
    if data is not None:
        response.pop("message")
        response["data"] = data
    return HttpResponse(json.dumps(response), content_type='text/javascript')

@csrf_exempt
def addUser(request):
    if request.method == 'POST':
        request_json = json.loads(request.body.decode("utf-8"))
        if 'username'  not in request_json or 'password' not in request_json:
            return createResponse("FAILURE", "Either username or password not present.")
        try:
            #for creating user
            User.objects.create_user(**request_json)
            return createResponse("success", 'User Created Successfully')
        except Exception as e:
            return createResponse("FAILURE",str(e))
    return createResponse("FAILURE","Get request is not allowed")

#Login and get the token for furher use
@csrf_exempt
def loginUser(request):
    if request.method == 'POST':
        request_json = json.loads(request.body.decode("utf-8"))
        if 'username'  not in request_json or 'password' not in request_json:
            return createResponse("FAILURE", "Either username or password not present.")
        username = request_json['username']
        password = request_json['password']
        try:
            user = authenticate(username = username, password = password)  # authenticate that user is exist or not
            if user:
                if user.is_active:
                    login(request, user)
                    token, _ = Token.objects.get_or_create(user=user)
                    data = {'status': 'SUCCESS',
                            'token':token.key,
                            'message': 'Login Successfully'}
                    return HttpResponse(json.dumps(data), content_type='text/javascript')
                else:
                    return createResponse("FAILURE","User is not active")
            else:
                return createResponse("FAILURE", "User does not exists")
        except Exception as d:
            return createResponse("FAILURE",str(d))
    return createResponse("FAILURE", "Not a valid request")

@csrf_exempt
@api_view(["POST"])
def addBox(request):

    if request.user.is_staff:
        global A1, V1, L1, L2
        request_data = json.loads(request.body.decode("utf-8"))
        # validation for the field
        if "length" not in request_data or "breadth" not in request_data or "height" not in request_data:
            return createResponse("FAILURE", "Length , breadth and hight must be in params")
        length = request_data["length"]
        breadth = request_data["breadth"]
        height = request_data["height"]
        area = 2 * (length * breadth + breadth * height + height * length)
        volume = length * breadth * height
        boxes = Box.objects.all()

        if boxes.count() == 0:
            Box.objects.create(length = length, breadth = breadth, height = height, area = area, volume = volume,  created_by = request.user)
        else:
            box_count = boxes.count()
            areas = list(boxes.values_list("area", flat=True))
            if (sum(areas) + area)/(box_count+1) > A1:
                return createResponse("FAILURE","Average area of the boxes shouldn't exceed " + str(A1))

            volumes = list(boxes.values_list("volume", flat=True))
            if (sum(volumes) + volume)/(box_count+1) > V1:
                return createResponse("FAILURE",  "Average volume of the boxes shouldn't exceed " + str(V1))

            week = datetime.today() - timedelta(days=7)
            box_week_count = Box.objects.filter(date_of_creation__gte = week).count()
            if box_week_count > L1:
                return createResponse("FAILURE", "Number of the boxes added in the week shouldn't exceed " + str(L1))

            box_user_week_count = Box.objects.filter(date_of_creation__gte = week, created_by = request.user).count()
            if box_user_week_count > L2:
                return createResponse("FAILURE", "Number of the boxes added by You in the week shouldn't exceed " + str(L2))

            #finally after checking all the valid condition we are going to add the box in the db
            Box.objects.create(length=length, breadth=breadth, height=height, area=area, volume=volume,
                               created_by=request.user)
        return createResponse("SUCCESS","Box is added successfully.")
    else:
        return createResponse("FAILURE", "You haven't permission to add the box.")


@csrf_exempt
@api_view(["POST"])
def updateBox(request):
    if request.user.is_staff:
        global A1,V1
        request_data = json.loads(request.body.decode("utf-8"))
        if "id" not in request_data or request_data["id"] == "":
            return createResponse("FAILURE", "Either id is null or id is not present")
        if Box.objects.filter(id = request_data["id"]).exists():
            box = Box.objects.get(id=request_data["id"])
            if "length" not in request_data:
                length = box.length
            else:
                length = request_data["length"]
            if "breadth" not in request_data:
                breadth = box.breadth
            else:
                breadth = request_data["breadth"]
            if "height" not in request_data:
                height  = box.height
            else:
                height = request_data["height"]

            area = 2*( length * breadth + breadth * height + height * length )
            volume = length * breadth * height
            boxes = Box.objects.all()
            boxes = boxes.exclude(id = request_data['id'])
            box_count = boxes.count()

            areas = list(boxes.values_list("area", flat=True))
            if (sum(areas) + area) / (box_count + 1) > A1:
                return createResponse("FAILURE","Average area of the boxes shouldn't exceed " + str(A1))

            volumes = list(boxes.values_list("volume", flat=True))
            if (sum(volumes) + volume) / (box_count + 1) > V1:
                return createResponse("FAILURE","Average volume of the boxes shouldn't exceed " + str(V1))
            box.length = length
            box.breadth = breadth
            box.height = height
            box.area = area
            box.volume = volume
            box.save()
            return createResponse("SUCCESS", "Box is Updated successfully.")
        else:
            return createResponse("FAILURE", "Box with given id is not exist.")
    else:
        return createResponse("FAILURE", "You haven't permission to update the box.")


@csrf_exempt
@api_view(["POST"])
def deleteBox(request):
    if request.user.is_staff:
        request_data = json.loads(request.body.decode("utf-8"))
        #if user doesn't send the id by mistake
        if "id" not in request_data or request_data["id"] == "":
            return createResponse("FAILURE", "Either id is null or id is not present")
        if Box.objects.filter(id=request_data["id"]).exists():
            box  = Box.objects.get(id = request_data["id"])
            # box will only deleted by the user who have created this
            if request.user != box.created_by:
                return createResponse("FAILURE", "Only creator of box can delete the box.")

            box.delete()
            return createResponse("SUCCESS", "Box is deleted successfully.")
        else:
            return createResponse("FAILURE", "Box with given id is not exist.")
    else:
        return createResponse("FAILURE", "You haven't permission to delete the box")


#This function will help in filtering the data on the basis of the filter applied by the user
#And if we pass the user then it will return the box created by the user
def filterFunction(filters, request, user = None):
    filter_query = {}
    #making the query dict for filtering
    for params in filters:
        #converting the string date time into python date
        if params == "date_of_creation":
            date = datetime.strptime(filters[params]["value"], "%d/%m/%Y").strftime("%Y-%m-%d")
            filter_query[params + "__" + filters[params]["condition"]] = date
        #so only allbox api will use this not the my box api where box will already filterd on the basis of username
        elif params == "created_by" and user is None:
            filter_query["created_by__username"] = filters[params]
        else:
            filter_query[params + "__" + filters[params]["condition"]] = filters[params]["value"]
    # for my box api
    if user is not None:
        filter_query["created_by"] = user
    boxes = Box.objects.filter(**filter_query)
    filtered_box = BoxSerializers(boxes,many=True, context={"request":request})
    return filtered_box.data

#Here any user can see the box but parameter veries
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def listBoxApiForAll(request):
    filter_data = json.loads(request.body.decode("utf-8"))
    return createResponse("SUCCESS", "",filterFunction(filter_data["filters"],request))


#This will return the users box list
@csrf_exempt
@api_view(["POST"])
def getMyBoxList(request):
    if request.user.is_staff:
        filter_data = json.loads(request.body.decode("utf-8"))
        return createResponse("SUCCESS", "", filterFunction(filter_data["filters"],request,request.user))
    else:
        return createResponse("FAILURE", "Only Valid for staff and login user")































