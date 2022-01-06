# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path
import math
from . import settings
from . import utils
from PIL import Image

userdir = os.path.join(settings.BASE_DIR, "data", "users")
imgdir = os.path.join(settings.BASE_DIR, "data", "images")
resdir = os.path.join(settings.BASE_DIR, "data", "jsons")
markdir = os.path.join(settings.BASE_DIR, "data", "marks")


class Player():
    def __init__(self, name='root'):
        self.name = name
        self.password = None
        self.data, self.done, self.half = [], [], []
        jsonfile = os.path.join(userdir, name + '.json')
        if os.path.exists(jsonfile):
            with open(jsonfile) as f:
                userInfo = json.load(f)
                self.password = userInfo['password']
                self.data = userInfo['data']
                self.done = list(userInfo['done'])
                self.half = list(userInfo['half'])

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

    def save(self, imgid, labels, marks, image_metadata, image_properties):
        labels = self.absLabel(imgid, labels)
        boxes, points = [], []
        for label in labels:
            if len(label) == 4:
                boxes.append(label)
            elif len(label) == 2:
                points.append(label)
        # print('utils - save - image json file:',os.path.join(resdir, imgid + '.json'))
        with open(os.path.join(resdir, imgid + '.json'), 'w+') as f:
            result = dict(
                img_id=imgid,
                metadata=image_metadata,
                properties=image_properties,
                human_num=len(labels),
                boxes=boxes,
                points=points
            )
            json.dump(result, f)
            # print('result:', result)
        with open(os.path.join(markdir, imgid + '.json'), 'w+') as f:
            json.dump(marks, f)
        # print('self.done1:', self.done)
        # print('self.half1:', self.half)
        # print('imgid:', imgid)
        marksum = sum(marks)
        if marksum <= 0:
            pass
        elif marksum < len(marks):
            if imgid in self.done:
                self.done.remove(imgid)
            if imgid not in self.half:
                self.half += [imgid]
        else:
            if imgid in self.half:
                self.half.remove(imgid)
            if imgid not in self.done:
                self.done += [imgid]
        with open(os.path.join(userdir, self.name + '.json'), 'w+') as f:
            json.dump(dict(
                password=self.password,
                data=self.data,
                done=list(self.done),
                half=list(self.half)
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

    def getMetadata(self, imgid):
        jsonpath = os.path.join(resdir, imgid + '.json')
        if not os.path.exists(jsonpath):
            return []
        with open(jsonpath) as f:
            js = json.load(f)
            if 'metadata' in js and isinstance(js['metadata'], list):
                image_metadata = js['metadata']
                # print('utils - getMetadata - image_metadata:', image_metadata)
            else:
                image_metadata = []
        return image_metadata

    def getProperties(self, imgid):
        jsonpath = os.path.join(resdir, imgid + '.json')
        if not os.path.exists(jsonpath):
            return []
        with open(jsonpath) as f:
            js = json.load(f)
            if 'properties' not in js or not isinstance(js['properties'], dict) or js['properties'] == {}:
                image_properties = getImageProperties(imgid)
                print('utils - getProperties - image_properties:', image_properties)
            else:
                image_properties = js['properties']
        return image_properties

    def absLabel(self, imgid, labels):
        img = Image.open(os.path.join(imgdir, imgid))
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
        img = Image.open(os.path.join(imgdir, imgid))
        w, h = img.size
        for i, label in enumerate(labels):
            for k, v in label.items():
                if 'x' in k:
                    label[k] = v / w
                elif 'y' in k:
                    label[k] = v / h
            labels[i] = label
        return labels


def getImageProperties(imgid):
    image_name = imgid
    img = Image.open(os.path.join(imgdir, imgid))
    image_width, image_height = img.size
    image_size = os.path.getsize(os.path.join(imgdir, imgid))
    image_size = round(image_size / 1024.)
    image_properties = dict(
        name=image_name,
        width=image_width,
        height=image_height,
        size=image_size
    )
    return image_properties


def init_image_jsons(imgid):
    with open(os.path.join(resdir, imgid + '.json'), 'w+') as f:
        result = dict(
            img_id=imgid,
            metadata=[],
            properties=getImageProperties(imgid),
            human_num=0,
            boxes=[],
            points=[]
        )
        json.dump(result, f)

    marks = [0 for _ in range(256)]
    with open(os.path.join(markdir, imgid + '.json'), 'w+') as f:
        json.dump(marks, f)


def check_new_images():
    print('Vérification des images ...')
    userdir = utils.userdir
    imgdir = utils.imgdir
    resdir = utils.resdir
    nb_users = 0
    all_data = []
    for userjs in os.listdir(userdir):
        with open(os.path.join(userdir, userjs)) as f:
            nb_users += 1
            userdata = json.load(f)
            print('user :', userjs, 'nb_images :', len(userdata['data']), 'images :', userdata['data'])
            for img in userdata['data']:
                all_data.append(img)
    print('nb_users:', nb_users, 'nb_total_images:', len(all_data), 'images :', all_data)

    all_images = [image for image in os.listdir(imgdir) if os.path.splitext(image)[1] in ['.jpg', '.png', '.jpeg']]
    print('Répertoire images - nb_images :', len(all_images), 'images :', all_images)
    images_to_add = [element for element in all_images if element not in all_data]

    if len(images_to_add) == 0:
        print('Aucune nouvelle image!')
    else:
        print("{} nouvelle(s) image(s) à affecter sur {} utilisateurs".format(len(images_to_add), nb_users), ' :',
              images_to_add)
        for image_filename in images_to_add:
            print("image_filename:", image_filename)
            # On rajoute l'extension dans l'id pour gerer les differents formats
            imgid = image_filename# Path(image_filename).stem
            init_image_jsons(imgid)

    nb_images_per_player = math.ceil(len(images_to_add) / nb_users)
    print("Nombre d'images par utilisateur :", nb_images_per_player)
    for userjs in os.listdir(userdir):
        user_name = userjs.replace('.json', '').lower()
        if user_name not in ["golden", "admin"]:
            with open(os.path.join(userdir, userjs)) as f:
                userdata = json.load(f)
                nb_images_add_to_current_player = 0
                while len(images_to_add) > 0 and nb_images_add_to_current_player < nb_images_per_player:
                    removed_image = images_to_add.pop(0)
                    userdata['data'].append(removed_image)
                    nb_images_add_to_current_player += 1
                    print('user :', userjs, 'nb:', nb_images_add_to_current_player, ' - add ', removed_image,
                          ' -img restant à affecter:', len(images_to_add))
            if nb_images_add_to_current_player > 0:
                with open(os.path.join(userdir, userjs), 'w+') as f:
                    json.dump(dict(userdata), f)
                print("Mise à jour de l'utilisateur : ", userjs, '- nb_images :', len(userdata['data']), 'images :',
                      userdata['data'])
            else:
                print("Aucune mise à jour de l'utilisateur : ", userjs)
