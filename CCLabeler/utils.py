# -*- coding: utf-8 -*-

import json
import os
from . import settings
from PIL import Image

userdir =  os.path.join(settings.BASE_DIR, "users")
imgdir = os.path.join(settings.BASE_DIR, "data", "images")
resdir = os.path.join(settings.BASE_DIR, "data", "jsons")
markdir = os.path.join(settings.BASE_DIR, "data", "marks")

class Player():
    def __init__(self, name='root'):
        self.name = name
        self.password = None
        self.data, self.done, self.half = [], set(), set()
        jsonfile = os.path.join(userdir, name + '.json')
        if os.path.exists(jsonfile):
            with open(jsonfile) as f:
                userInfo = json.load(f)
                self.password = userInfo['password']
                self.data = userInfo['data']
                self.done = set(userInfo['done'])
                self.half = set(userInfo['half'])
    
    def testPsd(self, psd=''):
        if self.password == None:
            return False
        return psd == self.password
    
    def labeling(self):
        label = "default"
        for imgid in self.data:
            if imgid not in self.done:
                label = imgid
                break
        return label
    
    def save(self, imgid, labels, marks):
        labels = self.absLabel(imgid, labels)
        boxes, points = [], []
        for label in labels:
            if len(label) == 4:
                boxes.append(label)
            elif len(label) == 2:
                points.append(label)

        with open(os.path.join(resdir, imgid + '.json'), 'w+') as f:
            json.dump(dict(
                img_id = imgid + '.jpg',
                human_num = len(labels),
                boxes = boxes,
                points = points
            ), f)
        with open(os.path.join(markdir, imgid + '.json'), 'w+') as f:
            json.dump(marks, f)

        marksum = sum(marks)
        if marksum <= 0:
            pass
        elif marksum < len(marks):
            self.done.discard(imgid)
            self.half.add(imgid)
        else:
            self.half.discard(imgid)
            self.done.add(imgid)

        with open(os.path.join(userdir, self.name + '.json'), 'w+') as f:
            json.dump(dict(
                password = self.password,
                data = self.data,
                done = list(self.done),
                half = list(self.half)
            ), f)
    
    def getWhich(self, thisid, which):
        if which == 0:
            return self.labeling()
        ans = thisid
        if which < 0:
            for imgid in self.data:
                if thisid == imgid:
                    break
                ans = imgid
        elif which > 0:
            flag = False
            for imgid in self.data:
                if flag:
                    ans = imgid
                    break
                if thisid == imgid:
                    flag = True
        return ans
    
    def getLabels(self, imgid):
        jsonpath = os.path.join(resdir, imgid + '.json')
        if not os.path.exists(jsonpath):
            return []
        with open(jsonpath) as f:
            js = json.load(f)
            boxes, points = js['boxes'], js['points']
        labels = boxes + points
        return self.relLabel(imgid, labels)

    
    def getMarks(self, imgid, context=True):
        markpath = os.path.join(markdir, imgid + '.json')
        if not os.path.exists(markpath):
            return [0 for _ in range(256)]
        with open(markpath) as f:
            if context:
                return json.load(f)
            else:
                return f.read()
    
    def absLabel(self, imgid, labels):
        img = Image.open(os.path.join(imgdir, imgid + '.jpg'))
        w, h = img.size
        for i, label in enumerate(labels):
            for k, v in label.items():
                if 'x' in k:
                    label[k] = v * w
                elif 'y' in k:
                    label[k] = v * h
            labels[i] = label
        return labels
    
    def relLabel(self, imgid, labels):
        img = Image.open(os.path.join(imgdir, imgid + '.jpg'))
        w, h = img.size
        for i, label in enumerate(labels):
            for k, v in label.items():
                if 'x' in k:
                    label[k] = v / w
                elif 'y' in k:
                    label[k] = v / h
            labels[i] = label
        return labels
