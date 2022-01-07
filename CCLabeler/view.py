from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect, reverse
from django.views.decorators.csrf import csrf_exempt

import json
from pathlib import Path
import os
from functools import reduce

from . import utils
from .forms import UploadFileForm, UnlockUserForm

Player = utils.Player


def login(request, errorlogin=0, nologin=0, locklogin=0):
    context = dict(error=errorlogin, nologin=nologin, locklogin=locklogin)
    return render(request, 'login.html', context)

def disconnect(request):
    name = request.POST.get('user')
    player = Player(name)
    player.disconnect()
    return HttpResponse(json.dumps({'success': True, 'message': 'user: %s disconnected'%name}), content_type='application/json')

def ping(request):
    name = request.POST.get('user')
    player = Player(name)
    locklogin = player.isLogged
    if locklogin != 1:
        print('User : %s ping'%name)
        return HttpResponse(json.dumps({'success': True, 'message': 'pong'), content_type='application/json')
    else:
        print('User : %s cannot pong'%name)

@csrf_exempt
def label(request):
    name = request.POST.get('user')
    if (name == None):
        return login(request)
    player = Player(name)
    imgid = request.POST.get('imgid')
    if imgid not in player.data:
        context = dict(
            username=name,
            cdata=makeTable(player),
        )
        return render(request, 'table.html', context)
    drawStack = json.dumps(player.getLabels(imgid))
    marks = player.getMarks(imgid, context=False)
    image_metadata = player.getMetadata(imgid)
    image_properties = player.getProperties(imgid)
    context = dict(
        imgid=imgid,
        image_metadata=json.dumps(image_metadata),
        image_properties=json.dumps(image_properties),
        user=name,
        drawStack=drawStack,
        labelMember=player.name,
        marks=marks,
        datalen=len(player.data),
        halflen=len(player.half),
        donelen=len(player.done)
    )
    print('view - label - context:', context)
    return render(request, 'label.html', context)


@csrf_exempt
def save(request, returnResponse=True):
    print('view - save - request.POST:', request.POST)

    name = request.POST.get('user')
    player = Player(name)
    # Test if user is connected for 1 hour or more
    locklogin = player.isLogged
    print("locklogin: %s"%locklogin)
    if locklogin == 1:
        return login(request, locklogin=1)

    imgid = request.POST.get('imgid')
    marks = json.loads(request.POST.get('marks'))
    labels = json.loads(request.POST.get('labels'))
    image_properties = player.getProperties(imgid)

    image_metadata = []
    pattern = request.POST.get("pattern")
    if pattern is not None:
        image_metadata.append("periodic_pattern")
    uniform = request.POST.get("uniform")
    if uniform is not None:
        image_metadata.append("uniform_distribution")
    density = request.POST.get("density")
    if density is not None and density != '':
        image_metadata.append("density_" + density)
    place = request.POST.get("place")
    if place is not None and place != '':
        image_metadata.append("place_" + place)
    angle = request.POST.get("angle")
    if angle is not None and angle != '':
        image_metadata.append("angle_" + angle)
    position = request.POST.get("position")
    if position is not None and position != '':
        image_metadata.append("position_" + position)

    player.save(imgid, labels, marks, image_metadata, image_properties)

    if returnResponse:
        context = dict(
            success=True,
            imgid=imgid,
            image_metadata=image_metadata,
            image_properties=image_properties,
            datalen=len(player.data),
            halflen=len(player.half),
            donelen=len(player.done)
        )
        print('view - save - context:', context)
        return HttpResponse(json.dumps(context), content_type='application/json')
    else:
        return player, imgid


@csrf_exempt
def jump(request):
    print('view - jump- request.POST:', request.POST)
    player, imgid = save(request, returnResponse=False)

    which = int(request.POST.get('which'))
    # print('view - jump - which:', which)
    nimgid = player.getWhich(imgid, which)

    ndrawStack = player.getLabels(nimgid)
    nmarks = player.getMarks(nimgid)
    nimage_metadata = player.getMetadata(nimgid)
    nimage_properties = player.getProperties(nimgid)

    context = dict(
        imgid=nimgid,
        image_metadata=nimage_metadata,
        image_properties=nimage_properties,
        drawStack=ndrawStack,
        marks=nmarks,
        datalen=len(player.data),
        halflen=len(player.half),
        donelen=len(player.done)
    )
    print('view - jump - context:', context)
    return HttpResponse(json.dumps(context), content_type='application/json')


@csrf_exempt
def generate_golden_dataframe(request):
    res = utils.generate_golden_dataframe(utils.userdir, utils.imgdir, utils.resdir, utils.datadir)
    if res:
        return HttpResponse("OK")
    else:
        return HttpResponse("KO")


# --------------------------Label Table ------------------------------------

def makeTable(player):
    cdata, row = [], []

    for d in player.data:
        if d in player.done:
            row.append(dict(data=d, tag=1))
        elif d in player.half:
            row.append(dict(data=d, tag=-1))
        else:
            row.append(dict(data=d, tag=0))
        if len(row) >= 10:
            cdata.append(row)
            row = []
    if len(row) > 0:
        cdata.append(row)
    return cdata


@csrf_exempt
def table(request):
    name = request.POST.get('user')
    pasd = request.POST.get('password')
    if (name == None):
        return login(request)

    player = Player(name)
    locklogin = player.isLogged
    print("locklogin: %s"%locklogin)
    if locklogin != 0: # User is connected
    # Neeed to connect again
        return login(request, locklogin=locklogin)
    if not player.testPsd(pasd):
        return login(request, errorlogin=1)


    form = UploadFileForm()
    form_unlock_user = UnlockUserForm()

    context = dict(
        username=name,
        cdata=makeTable(player),
        form=form,
        form_unlock_user=form_unlock_user,
        submitted=False
    )
    return render(request, 'table.html', context)


# ----------------------- Summary Info -------------------------

@csrf_exempt
def summary(request):
    userdir = utils.userdir
    labeldir = utils.resdir
    imgIds = []
    userInf = {'name': [], 'done': [], 'Nodone': [], 'label_amount': []}
    for userjs in os.listdir(userdir):
        userInf['name'].append(userjs.split('.')[0])
        with open(os.path.join(userdir, userjs)) as f:
            user = json.load(f)
            done_id = user['done']
            userInf['done'].append((len(done_id)))
            userInf['Nodone'].append(len(user['data']) - len(done_id))

        userSum = 0
        for id_ in done_id:
            with open(os.path.join(labeldir, id_ + '.json')) as f:
                userSum += json.load(f)['human_num']
        userInf['label_amount'].append(userSum)
        imgIds += done_id

    a = userInf['label_amount']
    b = userInf['done']
    c = userInf['name']
    d = userInf['Nodone']
    # order = sorted(range(len(userInf['label_amount'])), key=lambda k: userInf['label_amount'][k])
    [a, b, c, d] = zip(*sorted(zip(a, b, c, d), reverse=True))
    userInf['label_amount'] = list(a)
    userInf['done'] = list(b)
    userInf['name'] = list(c)
    userInf['Nodone'] = list(d)

    labelNum = []
    for idx in imgIds:
        with open(os.path.join(labeldir, idx + '.json')) as f:
            labelNum.append(json.load(f)['human_num'])

    labelNumSum = reduce(lambda a, b: a + b, labelNum)
    labelLevel = [0, 0, 0, 0, 0, 0, 0]
    for i in range(len(labelNum)):
        if labelNum[i] in range(0, 100):
            labelLevel[0] += 1
            continue
        if labelNum[i] in range(100, 300):
            labelLevel[1] += 1
            continue
        if labelNum[i] in range(300, 600):
            labelLevel[2] += 1
            continue
        if labelNum[i] in range(600, 1000):
            labelLevel[3] += 1
            continue
        if labelNum[i] in range(1000, 2000):
            labelLevel[4] += 1
            continue
        if labelNum[i] in range(2000, 4000):
            labelLevel[5] += 1
            continue
        if labelNum[i] >= 4000:
            labelLevel[6] += 1

    mlNum, mxNum = min(labelNum), max(labelNum)

    context = dict(
        imgNum=len(imgIds),
        LabelNum=labelNumSum,
        averageNum=f'{labelNumSum / len(imgIds):.2f}',
        mlNum=mlNum,
        mxNum=mxNum,
        userInf=userInf,
        p100=labelLevel[0],
        p300=labelLevel[1],
        p600=labelLevel[2],
        p1000=labelLevel[3],
        p2000=labelLevel[4],
        p4000=labelLevel[5],
        pabove4000=labelLevel[6]
    )
    return render(request, 'summary.html', context)


# def image_view(request):
#     if request.method == 'POST':
#         form = ImageForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             form.save()
#             return HttpResponse("Successful")
#     else:
#         form = ImageForm()
#     return render(request, 'image_upload.html', {'form': form})


def success(request):
    return HttpResponse('successfully uploaded')


@csrf_exempt
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            msg = ''
            for f in request.FILES.getlist('file'):  # myfile is the name of your html file button
                msg += handle_uploaded_file(f, str(f.name), str(request.POST['user']))
            # Redirect to previous page
            # TODO: pass user/password to prevent from asking it again
            # return redirect(request.META['HTTP_REFERER'])
            return HttpResponse(msg)
        else:
            return HttpResponse("error")


def handle_uploaded_file(file, filename, user):
    imgid = filename  # Path(filename).stem
    # Allocate the user
    path_user_json = Path(utils.userdir) / user
    with path_user_json.open(encoding="UTF-8") as source:
        user_json = json.load(source)
    if imgid in user_json["data"]:
        return "The image %s exists in %s \n" % (filename, user)
    user_json["data"] += [imgid]
    with path_user_json.open("w", encoding="UTF-8") as target:
        json.dump(user_json, target)

    # Save image
    with open(Path(utils.imgdir) / filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    utils.init_image_jsons(imgid)

    return "Success"
