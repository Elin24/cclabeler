# 人群计数标注工具

这个repo是一个用于在图像中标注行人的，基于web的，可以快速部署的标注工具。其目前可以提供 *框标注* 和 *点标注* 两种方法。该工具也可以迁移到其他标注相同目标的项目中去，例如车辆标注、人脸框定等。

在标注过程中，我们的工具自动将整张图片分割成 $16 \times 16$ 的小区块。使得标注着可以在原图的5个尺度下（1，2，4，8，16）标注目标，用于应对标注过程中人头点标尺度变化问题。而之所以要划分区块而不是完全自由尺度变化，则是巍峨了防止漏标和多标的情况。划分区块以后就可以设置任意区块是否标注完成。提升标注的速度和质量。更加具体的展示参见我们的[标注视频](https://www.youtube.com/watch?v=U4Vc6bOPxm0&authuser=0)。

目前该应用仅支持单类别标注，多类别标注会在后期在该代码的基础上拓展出来。

![exhibitation](readmeimg/cclabel.jpg)

## Request

- Python 3.+
- Django (`pip install django`)

## 如何运行

1. 将该repository 克隆到本地工作区: `git clone https://github.com/Elin24/cclabeler.git`
2. 将待标注的图片放入 `data/images` 下，`data`目录结构如下。初始时，jsons和marks中不包含文件，其中国的文件会在标注过程中产生。其中jsons文件夹下的文件即为标注结果。

> ```
> data
>   ├─images
>   │      1.jpg
>   │      2.jpg
>   │      3.jpg
>   │      default.jpg (在所有文件标注完成后展示的文件)
>   │
>   ├─jsons
>   │      1.json
>   │      2.json
>   │      3.json
>   │
>   └─marks
>          1.json
>          2.json
>          3.json
> ```
3. 设置标注人员: 
> 1. 在`user/`目录下按照`test.json`设置每一个标注人员的信息和他将要标注的图片集
> 2. 文件名即为用户的用户名（例如 `test.json`表示用户名是*test*）
> 3. json文件中的`password`为登录口令
> 4. `data`是一个列表，存储了所有该用户需要标注的图像名称
> 5. `done`是一个列表，表示该用户已经完成标注的图像名称（初始时可设置为空列表）
> 6. `half`是一个列表，表示该用户正在标注的图像名称（初始时可设置为空列表）

4. 进入主目录并运行django服务: `python manage.py runserver 0.0.0.0:8000`
6. 登录账户，开始标注。

## 标注过程中的快捷键

- `ctrl+滚轮`：放大缩小图片
- `R/F`：放大缩小图片，和`ctrl+滚轮`效果相同，`R`为放大，`F`为缩小
- `WASD`：移动待标注区域
- `C/V`：标记当前区域为 *已标注/未标注*。与界面右边的`Marded as labeled`/`Marked as unlabeled`作用分别对应
- `ctrl+Z`：撤销标注操作
- `ctrl+Y`：恢复刚才的撤销操作
- `crrl+S`：保存当前标注状态到后台（实际上每20s会自动保存一次）


## 标注情况展示

登录 [http://localhost:8000/summary](http://localhost:8000/summary) 可以获得目前所有标注人员的情况和进度。

## 引用

如果觉得我们的工具对你们的项目或者工作有用，请引用：
```
@article{gao2020nwpu,
  title={NWPU-Crowd: A Large-Scale Benchmark for Crowd Counting},
  author={Wang, Qi and Gao, Junyu and Lin, Wei and Li, Xuelong},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
  doi={10.1109/TPAMI.2020.3013269},
  year={2020}
}
```