from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import os
from functools import reduce

from . import utils
Player = utils.Player

def login(request, errorlogin=0, nologin=0):
    context = dict(error=errorlogin, nologin=nologin)
    return render(request, 'login.html', context)

@csrf_exempt
def label(request):
    name = request.POST.get('user')
    imgid = request.POST.get('imgid')
    if (name == None):
        return login(request)
    player = Player(name)
    if imgid not in player.data:
        context = dict(
            username=name,
            cdata = makeTable(player),
        )
        return render(request, 'table.html', context)
    drawStack = json.dumps(player.getLabels(imgid))
    marks = player.getMarks(imgid, context=False)
    context = dict(
        imgid = imgid,
        user = name,
        drawStack = drawStack,
        labelMember = player.name,
        marks = marks,
        datalen = len(player.data),
        halflen = len(player.half),
        donelen = len(player.done)
    )
    return render(request, 'label.html', context)

@csrf_exempt
def save(request, returnResponse=True):
    name = request.POST.get('user')
    player = Player(name)
    imgid = request.POST.get('imgid')
    marks = json.loads(request.POST.get('marks'))
    labels = json.loads(request.POST.get('labels'))
    player.save(imgid, labels, marks)
    if returnResponse:
        context = dict(
            success=True,
            datalen = len(player.data),
            halflen = len(player.half),
            donelen = len(player.done)
        )
        return HttpResponse(json.dumps(context), content_type='application/json')
    else:
        return player, imgid

@csrf_exempt
def jump(request):
    player, imgid = save(request, returnResponse=False)
    which = int(request.POST.get('which'))
    nimgid = player.getWhich(imgid, which)
    ndrawStack = player.getLabels(nimgid)
    nmarks = player.getMarks(nimgid)
    context = dict(
        imgid = nimgid,
        drawStack = ndrawStack,
        marks = nmarks,
        datalen = len(player.data),
        halflen = len(player.half),
        donelen = len(player.done)
    )
    return HttpResponse(json.dumps(context), content_type='application/json')

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
    # print(name)
    if (name == None):
        return login(request)
    player = Player(name)
    if not player.testPsd(pasd):
        return login(request, errorlogin=1)
    context = dict(
        username=name,
        cdata = makeTable(player)

    )

    return render(request, 'table.html', context)

# ----------------------- Summary Info -------------------------

@csrf_exempt
def summary(request):
    userdir = utils.userdir
    labeldir = utils.resdir
    imgIds = []
    userInf= {'name':[], 'done':[], 'Nodone':[], 'label_amount':[]}
    for userjs in os.listdir(userdir):
        userInf['name'].append(userjs.split('.')[0])
        with open(os.path.join(userdir, userjs)) as f:
            user = json.load(f)
            done_id = user['done']
            userInf['done'].append((len(done_id)))
            userInf['Nodone'].append(len(user['data'])-len(done_id))

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
    #order = sorted(range(len(userInf['label_amount'])), key=lambda k: userInf['label_amount'][k])
    [a,b,c,d] = zip(*sorted(zip(a, b, c, d), reverse=True))
    userInf['label_amount'] = list(a)
    userInf['done'] = list(b)
    userInf['name'] = list(c)
    userInf['Nodone'] = list(d)

    labelNum = []
    for idx in imgIds:
        with open(os.path.join(labeldir, idx + '.json')) as f:
            labelNum.append(json.load(f)['human_num'])


    labelNumSum = reduce(lambda a, b: a + b, labelNum)
    labelLevel = [0,0,0,0,0,0,0]
    for i in range(len(labelNum)):
        if labelNum[i] in range(0,100):
            labelLevel[0] += 1
            continue
        if labelNum[i] in range(100,300):
            labelLevel[1] += 1
            continue
        if labelNum[i] in range(300,600):
            labelLevel[2] += 1
            continue
        if labelNum[i] in range(600,1000):
            labelLevel[3] += 1
            continue
        if labelNum[i] in range(1000,2000):
            labelLevel[4] += 1
            continue
        if labelNum[i] in range(2000,4000):
            labelLevel[5] += 1
            continue
        if labelNum[i] >=4000:
            labelLevel[6] += 1

    mlNum, mxNum = min(labelNum), max(labelNum)

    context = dict(
        imgNum = len(imgIds),
        LabelNum = labelNumSum,
        averageNum = f'{labelNumSum / len(imgIds):.2f}',
        mlNum = mlNum,
        mxNum = mxNum,
        userInf = userInf,
        p100 = labelLevel[0],
        p300 = labelLevel[1],
        p600 = labelLevel[2],
        p1000 = labelLevel[3],
        p2000 = labelLevel[4],
        p4000 = labelLevel[5],
        pabove4000 = labelLevel[6]
    )
    return render(request, 'summary.html', context)
