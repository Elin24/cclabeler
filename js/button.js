/******* butten event ********/

function baseMove(noreloc, reloc, step) {
    var current = markStatus.current;
    var dl = current.length - 1;
    if (dl == 0) return;
    if (noreloc.includes(current[dl])) {
        current = current.substring(0, dl) + String(parseInt(current[dl]) - step);
    } else {
        var now = dl;
        while (now > 0 && reloc.includes(current[now])) now--;
        if (now > 0) {
            var repAlpha = parseInt(current[now]);
            current = current.substring(0, now) + String(repAlpha - step) + current.substring(now + 1, dl + 1);
            while (++now <= dl) {
                repAlpha = parseInt(current[now]) + step;
                current = current.substring(0, now) + String(repAlpha) + current.substring(now + 1, dl + 1);
            }
        }
    }
    markStatus.current = current;
}

/******* move step ********/

function moverefresh() {
    drawGrid();
    resizeImage();
}

function move(direction) {
    // push 'W': up
    if (direction == 'W') {
        baseMove("34", "12", 2);
    }
    // push 'A': left
    else if (direction == 'A') {
        baseMove("24", "13", 1);
    }
    // push 'S': down
    else if (direction == 'S') {
        baseMove("12", "34", -2);
    }
    // push 'D': right
    else if (direction == 'D') {
        baseMove("13", "24", -1);
    }
    // push 'R': back
    else if (direction == 'R') {
        var current = markStatus.current;
        current = current.length <= 1 ? "1" : current.substring(0, current.length - 1);
        markStatus.current = current;
    }
    // push 'F': forward
    else if (direction == 'F') {
        var current = markStatus.current;
        current += (current.length < treeDepth + 1) ? "1" : "";
        markStatus.current = current;
    }
    moverefresh();
}

function changeImgMain(_which) {
    var sendinfo = {
        user: user,
        imgid: imgpath.split('/')[1].split('.')[0],
        marks: JSON.stringify(markStatus.marks),
        labels: JSON.stringify(drawStack.stack),
        which: _which
    };
    $.post('/jump', sendinfo, function (result) {
        imgpath = "static/" + result.imgid + ".jpg";
        opeStack.clear();
        drawStack = new DrawStack(result.drawStack);
        markStatus = new MarkStatus(result.marks);
        loadImage();
        drawGrid();
        console.log(result);
        drawSchedule(result.donelen, result.halflen, result.datalen);
    });
}

function changeImg(_which) {
    if (markStatus.marks.reduce((a, b) => a + b, 0) == markStatus.marks.length) {
        $('#finished').removeClass('hide');
        setTimeout(function () {
            $('#finished').addClass('hide');
            changeImgMain(_which);
        }, 500);
    } else {
        $('#unfinished').removeClass('hide');
        setTimeout(function () {
            $('#unfinished').addClass('hide');
            changeImgMain(_which);
        }, 500);
    }
}

$(document).keydown(function (event) {
    if (event.keyCode == 46 && labelStage == 'rectify' && curLabelForm != null) {
        drawStack.remove(rectifyIdx);
        rectifyIdx = -1, curLabelForm = null;
        rectifyOperation();
    }
    if (event.keyCode == 188) {
        changeImg(-1);
    } else if (event.keyCode == 190) {
        changeImg(1);
    } else if (event.keyCode == 32) {
        changeImg(0);
    }
    var keyCode = String.fromCharCode(event.keyCode);
    if ('ASDWRF'.includes(keyCode)) {
        move(keyCode);
    } else if (keyCode == 'C') {
        markStatus.markFunc(1);
    } else if (keyCode == 'V') {
        markStatus.markFunc(0);
    }
});

$.ctrl = function (key, callback, args) {
    var isCtrl = false;
    $(document).keydown(function (e) {
        if (!args) args = [];

        if (e.ctrlKey) isCtrl = true;
        if (e.keyCode == key.charCodeAt(0) && isCtrl) {
            callback.apply(this, args);
            return false; //you can remove this line if you need bookamrk
        }
    }).keyup(function (e) {
        if (e.ctrlKey) isCtrl = false;
    });
};

$.ctrl('Z', function () {
    var ope = opeStack.back();
    if (ope == null) return;
    if (ope.stackType == 'mark') {
        markStatus = ope.clone();
        drawGrid();
    } else if (ope.stackType == 'draw') {
        drawStack = ope.clone();
        runDraw();
    }
});

$.ctrl('Y', function () {
    var ope = opeStack.forward();
    if (ope == null) return;
    if (ope.stackType == 'mark') {
        markStatus = ope.clone();
        drawGrid();
    } else if (ope.stackType == 'draw') {
        drawStack = ope.clone();
        runDraw();
    }
});
$.ctrl('S', function () {
    var sendinfo = {
        user: user,
        imgid: imgpath.split('/')[1].split('.')[0],
        marks: JSON.stringify(markStatus.marks),
        labels: JSON.stringify(drawStack.stack)
    };
    $.post('/save', sendinfo, function (result) {
        if (result.success) {
            var savediv = $('#save');
            drawSchedule(result.donelen, result.halflen, result.datalen);
            savediv.removeClass('hide');
            setTimeout(() => { savediv.addClass('hide'); }, 1000);
        }
    });
})

function changebtn(btn) {
    var btns = ["opbox", "oppoint", "oprectify"];
    var selc = 'btn-primary', noselc = 'btn-info';
    for (var i = 0; i < 3; i++) {
        var button = $('#' + btns[i]);
        if (button.hasClass(selc)) {
            button.removeClass(selc);
            button.addClass(noselc);
        }
    }
    $('#' + btn).removeClass(noselc);
    $('#' + btn).addClass(selc);
}

$('#opbox').click(function () {
    changebtn('opbox');
    labelStage = 'label';
    curLabelForm = new Box();
    labelMouse();
    drawStack.runStack();
});
$('#oppoint').click(function () {
    changebtn('oppoint');
    labelStage = 'label';
    curLabelForm = new Point();
    labelMouse();
    drawStack.runStack();
});
$('#oprectify').click(function () {
    changebtn('oprectify');
    labelStage = 'rectify';
    rectifyMouse();
    curLabelForm = null;
});

/************ mouse event  *************/

$(document).ready(function () {
    $('#cvs').on('mousewheel', function (event) {
        event.preventDefault();
        if (event.ctrlKey) {
            var current = markStatus.current;
            var pos = MousePos(event);
            var zoomCenter = new Point(pos.x, pos.y);
            var l = 1 << treeDepth;
            zoomCenter = zoomCenter.normalize(...imgStatus.sizePara());
            var x = Math.floor(l * zoomCenter.x), y = Math.floor(l * zoomCenter.y);
            var cl = current.length;
            current = "1";
            var measure = () => {
                var lstc = 1; l >>= 1;
                if (x >= l) lstc += 1, x -= l;
                if (y >= l) lstc += 2, y -= l;
                return String(lstc);
            };
            while (current.length < cl) current += measure();
            if (event.originalEvent.wheelDelta > 0) {
                // zoom in
                current += (current.length < treeDepth + 1) ? measure() : "";
            } else {
                // zoom out
                current = current.length <= 1 ? "1" : current.substring(0, current.length - 1);
            }
            markStatus.current = current;
        } else if (event.shiftKey) {
            if (event.originalEvent.wheelDelta > 0) {
                // left
                baseMove("24", "13", 1);
            } else {
                // right
                baseMove("13", "24", -1);
            }
        } else {
            if (event.originalEvent.wheelDelta > 0) {
                // up
                baseMove("34", "12", 2);
            } else {
                // down
                baseMove("12", "34", -2);
            }
        }
        moverefresh();
    });
    $('#grid').on('mousewheel', function (event) {
        event.preventDefault();
        if (event.ctrlKey) {
            var current = markStatus.current;
            if (event.originalEvent.wheelDelta > 0) {
                current += (current.length < treeDepth + 1) ? "1" : "";
            } else {
                current = current.length <= 1 ? "1" : current.substring(0, current.length - 1);
            }
            markStatus.current = current;
            moverefresh();
        }
    });
    $('#grid').on('click', function (event) {
        var current = markStatus.current;
        var pos = MousePos(event, this);
        var l = 1 << treeDepth;
        var x = Math.floor(pos.x / this.width * l), y = Math.floor(pos.y / this.height * l);
        var cl = current.length, lstc;
        current = "1";
        while (current.length < cl) {
            lstc = 1; l >>= 1;
            if (x >= l) lstc += 1, x -= l;
            if (y >= l) lstc += 2, y -= l;
            current += String(lstc);
        }
        markStatus.current = current;
        moverefresh();
    })
});

/************ mark event  *************/

$('#mark').click(() => {
    markStatus.markFunc(1);
});
$('#unmark').click(() => {
    markStatus.markFunc(0);
});
$('#lastimg').click(() => {
    changeImg(-1);
});
$('#nextimg').click(() => {
    changeImg(1);
});
$('#loadimg').click(() => {
    changeImg(0);
});

/************ point size and color  *************/

function changeLineWidth() {
    labelLineWidth = wslider.getValue();
    runDraw();
}

var wslider = $("#wslider").slider({tooltip: 'hide'})
    .on('slide', changeLineWidth)
    .data('slider');

$('#pc-red').click(()=>{
    labelLineColor = 'red';
    runDraw();
});
$('#pc-green').click(()=>{
    labelLineColor = '#00CC99';
    runDraw();
});
$('#pc-orange').click(()=>{
    labelLineColor = '#FF6600';
    runDraw();
});