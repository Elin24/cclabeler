/******************** draw grid ****************/

// var label = [1, 0, 1, 0];
// var current = 0;

function clip(w, h) {
    var cy = 0, cx = 0, cw = w * 2, ch = h * 2;
    var current = markStatus.current;
    for (var i = 0; i < current.length; i++) {
        cw >>= 1; ch >>= 1;
        if (current[i] == '2') cx += cw;
        else if (current[i] == '3') cy += ch;
        else if (current[i] == '4') cx += cw, cy += ch;
    }
    return [cy, cx, cw, ch];
}

function drawGrid() {
    var grid = document.getElementById("grid");
    var gtx = grid.getContext('2d');

    // clear grid
    gtx.clearRect(0, 0, grid.width, grid.height);

    var atomNum = 1 << treeDepth;
    var w = grid.width / atomNum, h = grid.height / atomNum;
    if (markStatus.marks.length != atomNum * atomNum) {
        console.log('lable length is', markStatus.marks.length, ', but atomNum is', atomNum);
        return;
    }

    var colors = [
        'rgba(149, 165, 166,   1)', //notlabel
        'rgba( 22, 160, 133,   1)', //haslabel
        'rgba(243, 156,  18, 0.5)'  //curlabel
    ];
    // all grids
    for (var i = 0; i < atomNum; i++) {
        for (var j = 0; j < atomNum; j++) {
            var color = colors[markStatus.marks[i * atomNum + j]];
            drawRect(gtx, i * w, j * h, w, h, '#fff', color, 4);
        }
    }
    var clipara = clip(grid.width, grid.height);
    var cr = clipara[0], cc = clipara[1], cw = clipara[2], ch = clipara[3];

    // current grids
    color = colors[2];
    if (cw > grid.width / atomNum) {
        cw /= 2, ch /= 2;
        var bias = [[0, 0], [cw, 0], [0, ch], [cw, ch]];
        for (var i = 0; i < 4; i++) {
            drawRect(gtx, cc + bias[i][0], cr + bias[i][1], cw, ch, '#000', color, 1);
        }
    }
    else {
        drawRect(gtx, cc, cr, cw, ch, '#000', color, 1);
    }
}

/******************** load image ****************/

function resizeImage() {
    var clipara = clip(imgStatus.image.width, imgStatus.image.height);
    var cy = clipara[0], cx = clipara[1], cw = clipara[2], ch = clipara[3];
    var ratew = (canvas.width - imgStatus.border) / cw;
    var rateh = (canvas.height - imgStatus.border) / ch;
    var rate = Math.min(rateh, ratew);
    imgStatus.scale = rate;
    var ox = (canvas.width - cw * rate) / 2;
    var oy = (canvas.height - ch * rate) / 2;
    imgStatus.offsetx = ox - cx * rate;
    imgStatus.offsety = oy - cy * rate;

    runDraw();
}

function loadImage() {
    imgStatus.image = new Image();
    imgStatus.image.src = imgpath;
    imgStatus.image.onload = function () {
        resizeImage();
    };
}

/****************** label *****************/

function labelOperation(e = null, start = false) {
    drawStack.runStack();
    if (e == null) return;
    var loc = MousePos(e);
    if (curLabelForm.type[0] == 'B') {
        curLabelForm.ex = loc.x;
        curLabelForm.ey = loc.y;
        if (start) {
            curLabelForm.sx = loc.x;
            curLabelForm.sy = loc.y;
        }
    } else if (curLabelForm.type[0] == 'P') {
        curLabelForm.x = loc.x;
        curLabelForm.y = loc.y;
    }
    if (labelStatus) {
        curLabelForm.draw();
    }
}

function labelStart(e) {
    console.log(e.which);
    if (labelStatus || e.which == 3) return;
    labelStatus = true;
    labelOperation(e, true);
}
function labelMove(e) {
    if (!labelStatus) return;
    labelOperation(e);
}

function labelEnd(e) {
    if (!labelStatus || e.which == 3) return;
    labelStatus = false;
    if (curLabelForm.type != 'Box' || (
        Math.abs(curLabelForm.ex - curLabelForm.sx) > labelLineWidth &&
        Math.abs(curLabelForm.ey - curLabelForm.sy) > labelLineWidth
    )) {
        opeStack.pushStack(drawStack.clone());
        drawStack.pushStack(curLabelForm);
    }
    labelOperation(e);
}
function labelMouse() {
    canvas.onmousedown = labelStart;
    canvas.onmousemove = labelMove;
    canvas.onmouseup = labelEnd;
}

/****************** rectify *****************/

function rectifyOperation(loc = null) {
    drawStack.runStack();
    if (curLabelForm != null) {
        if(loc != null) {
            switch (rectifyType) {
                case 1:
                    curLabelForm.sy = loc.y; break;
                case 2:
                    curLabelForm.ex = loc.x; break;
                case 3:
                    curLabelForm.ey = loc.y; break;
                case 4:
                    curLabelForm.sx = loc.x; break;
                case 5:
                    curLabelForm.x = loc.x; curLabelForm.y = loc.y; break;
                default:
                    rectifyType = 0;
            }
        }
        curLabelForm.draw(true);
    }
}

function rectifyStart(e) {
    var loc = MousePos(e);
    var closeType = 0;
    if (curLabelForm != null) {
        closeType = curLabelForm.nearby(loc.x, loc.y);
    }
    if (!rectifyType && closeType) {
        rectifyType = closeType;
        opeStack.pushStack(drawStack.clone());
        drawStack.remove(rectifyIdx);
        rectifyOperation(loc);
    } else {
        var _rectifyIdx = drawStack.nearby(loc.x, loc.y);
        if(_rectifyIdx >= 0) {
            rectifyIdx = _rectifyIdx;
            curLabelForm = drawStack.label(rectifyIdx, true);
            rectifyOperation();
        }    
    }
}

function rectifyMove(e) {
    var loc = MousePos(e);
    var _rectifyIdx = drawStack.nearby(loc.x, loc.y);
    if (_rectifyIdx >= 0) canvas.style.cursor = 'move';
    else canvas.style.cursor = 'default';
    
    if (curLabelForm != null) {
        var closeType = curLabelForm.nearby(loc.x, loc.y);
        if(closeType) canvas.style.cursor = cursors[closeType];
        if (rectifyType) {
            rectifyOperation(loc);
        }
    }
}

function rectifyEnd(e) {
    if(e.which == 3) return ;
    var loc = MousePos(e);
    if(curLabelForm != null) {
        console.log(rectifyType, rectifyIdx);
        if (rectifyType > 0) {
            drawStack.insert(rectifyIdx, curLabelForm);
            rectifyOperation(loc);
        }
        rectifyType = 0;
    }
}

function rectifyMouse() {
    canvas.onmousedown = rectifyStart;
    canvas.onmousemove = rectifyMove;
    canvas.onmouseup = rectifyEnd;
}
