# Crowd Counting Labeler

Fork from https://github.com/Elin24/cclabeler

Crowd Counting Labeler is a tool for labeling pedestrians in a images. It is a web application which could be deployed quickly, and provides two types label: `box` and `point`.

At present, it does not support multi-class labeling, which would be a future function.

![exhibitation](readmeimg/cclabel.jpg)

## How to run demo

1. clone the repository to local workspace:
> `git clone https://github.com/fabricejourdan/cclabeler.git`
2. create Python environment with Django and Pillow:
> `conda create --name cclabeler python=3.9.7 django=4.0 pillow=8.4.0`
3. cd to the directory, run django server:
> `python manage.py runserver 0.0.0.0:8000`
4. login to the address in browser and enjoy it.
> `http://localhost:8000/`

## deploy new image data for labeling

Image data should be put in `data/` fold
```
├─images (contain images to label)
│      1.jpg
│      2.jpg
│      3.jpg
│      .....
│
├─jsons (for each image, json file containing selected points and boxes)
│      1.json
│      2.json
│      3.json
|      .....
│
└─marks
        1.json
        2.json
        3.json
        .....
```

## Set of examples for Demo

1. Three users

user1 , user2 and golden

Password are define in the file /users/{username}.json

2. Each user have a set of images from ShanghaiTech_B dataset

user1 : 18 images from ShanghaiTech_B 

user2 : 2 images from ShanghaiTech_B

golden : 10 images from CityUHK-X-BEV dataset (https://github.com/daizhirui/CityUHK-X-BEV)

For each user, the list of images to label is define in the file /users/{username}.json

## Summary (statistics)

loin [http://localhost:8000/summary](http://localhost:8000/summary) for summary.
