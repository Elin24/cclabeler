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

1. Two users

userI where I=1 and 2

Password are define in /users/userI.json

2. Each user have 10 images from ShanghaiTech_B dataset

For the labeller userI, all images are listed in user in /users/userI.json

For user1 : IMG_6.jpg, IMG_17.jpg, IMG_52.jpg, IMG_57.jpg, IMG_60.jpg, IMG_76.jpg, IMG_83.jpg, IMG_197.jpg, IMG_229.jpg, IMG_255.jpg

For user22 : IMG_294.jpg, IMG_308.jpg, IMG_319.jpg, IMG_328.jpg, IMG_339.jpg, IMG_345.jpg, IMG_350.jpg, IMG_389.jpg, IMG_397.jpg


## Summary (statistics)

loin [http://localhost:8000/summary](http://localhost:8000/summary) for summary.
