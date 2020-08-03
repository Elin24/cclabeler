# Crowd Counting Labeler

Crowd Counting Labeler is a tool for labeling pedestrians in a images. It is a web application which could be deployed quickly, and provides two types label: `box` and `point`.

At present, it does not support multi-class labeling, which would be a future function.

![exhibitation](readmeimg/cclabel.jpg)

## Request

- Python 3.+
- Django (`pip install django`)

## How to run demo

1. clone the repository to local workspace:
> `git clone https://github.com/Elin24/cclabeler.git`
2. cd to the directory, run django server:
> `python manage.py runserver 0.0.0.0:8000`
3. login to the address in browser and enjoy it.

## deploy new image data for labeling

Image data should be put in `data/` fold
```
├─images
│      1.jpg
│      2.jpg
│      3.jpg
│      default.jpg
│
├─jsons
│      1.json
│      2.json
│      3.json
│
└─marks
        1.json
        2.json
        3.json
```

## Summary

loin [http://localhost:8000/summary](http://localhost:8000/summary) for summary.
