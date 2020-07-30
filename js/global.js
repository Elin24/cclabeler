/******************** glbal variable ****************/

const treeDepth = 4;

/****************** operation stack *****************/

opeStack = {
    stack: new Array(),
    length: 0,
    pushStack: function (status) {
        var dstack = status.clone();
        if (this.length < this.stack.length) {
            this.stack = this.stack.splice(0, this.length);
        }
        this.stack.push(dstack);
        this.length++;
        if(this.length > 200) {
            this.stack.splice(0, 1);
            this.length--;
        }
    },
    popStack: function () {
        this.length--;
        if (this.length < 0) this.length = 0;
    },
    forward: function () {
        if(this.length >= this.stack.length) return null;
        this.length++;
        return this.topStack();
    },
    back: function () {
        if(this.length <= 0) return null;
        var ope = this.topStack();
        this.popStack();
        return ope;
    },
    topStack: function () {
        var topOne = null;
        if (this.length > 0) topOne = this.stack[this.length - 1];
        return topOne;
    },
    clear: function() {
        this.stack = new Array();
        this.length = 0;
    }
}

/****************** mark status *****************/

function MarkStatus(_marks = null, _current=null) {
    this.marks = new Array((1 << treeDepth) * (1 << treeDepth));
    this.current = "1";
    if (_marks != null) {
        for (var i = 0; i < _marks.length; i++) {
            this.marks[i] = _marks[i];
        }
    } else {
        for(var i = 0; i < this.marks.length; i++) {
            this.marks[i] = 0;
        }
    }
    if (_current != null) this.current = _current;
}
MarkStatus.prototype.clone = function () {
    return new MarkStatus(this.marks, this.current);
}
MarkStatus.prototype.markFunc = function(mark) {
    opeStack.pushStack(this.clone());
    var l = 1 << treeDepth;
    var ws = 0, w = l,
        hs = 0, h = l;
    for(var i = 1; i < this.current.length; i++) {
        w >>= 1, h >>= 1;
        switch(this.current[i]) {
            case '1': 
                break;
            case '2': ws += w;
                break;
            case '3': hs += h;
                break;
            case '4': ws += w, hs += h;
        }
    }
    for(var i = 0; i < w; i++) {
        for(var j = 0; j < h; j++) {
            markStatus.marks[(i + ws) * l + (j + hs)] = mark;
        }
    }
    drawGrid();
}
MarkStatus.prototype.stackType = 'mark';

var markStatus = new MarkStatus(initMarkStatus);

/******************** init and resize ****************/

var canvas = document.getElementById("cvs");
var ctx = canvas.getContext('2d');
var imgStatus = {
    border: 400,
    image: null,
    offsetx: 0,
    offsety: 0,
    scale: 0,
    draw: function () {
        drawRect(ctx, 0, 0, canvas.width, canvas.height, '#000', 'rgba(52, 73, 94, 1)', 1);
        if (this.image != null) {
            img = this.image;
            ctx.drawImage(this.image,
                0, 0, img.width, img.height,
                this.offsetx, this.offsety, this.scale * img.width, this.scale * img.height);
            var notmain = 'rgba(52, 73, 94, 0.6)';
            var cw = this.image.width << 1,
                ch = this.image.height << 1,
                l = markStatus.current.length;
            while (l--) cw >>= 1, ch >>= 1;
            var ox = (canvas.width - cw * this.scale) / 2,
                oy = (canvas.height - ch * this.scale) / 2;
            cw *= this.scale, ch *= this.scale;
            drawRect(ctx, 0, 0, ox, canvas.height, null, notmain, 1);
            drawRect(ctx, ox, 0, canvas.width - ox, oy, null, notmain, 1);
            drawRect(ctx, ox + cw, oy, canvas.width - ox - cw, ch, null, notmain, 1);
            drawRect(ctx, ox, oy + ch, canvas.width, canvas.height, null, notmain, 0);
        }
    },
    playW: function () { return this.scale * this.image.width; },
    playH: function () { return this.scale * this.image.height; },
    sizePara: function () { return [this.offsetx, this.offsety, this.playW(), this.playH()]; },
}

function drawRect(context, x, y, width, height, borderColor = null, fillColor = null, borderWidth = 1) {
    context.beginPath();
    context.moveTo(x, y);
    context.lineTo(x + width, y);
    context.lineTo(x + width, y + height);
    context.lineTo(x, y + height);
    context.closePath();
    if (fillColor != null) {
        context.fillStyle = fillColor;
        context.fill();
    }
    if (borderColor != null) {
        context.lineWidth = borderWidth;
        context.strokeStyle = borderColor;
        context.stroke();
    }
}

function drawPoint(context, x, y, color = '#f00', width = 1) {
    context.beginPath();
    context.lineCap = 'round';
    context.moveTo(x, y);
    context.lineTo(x, y);
    context.closePath();
    context.lineWidth = width;
    context.strokeStyle = color;
    context.stroke();
}

function drawLine(context, x, y, color = '#f00', width = 1) {
    context.beginPath();
    context.lineCap = 'round';
    context.moveTo(x, y);
    context.lineTo(x + 200, y);
    context.closePath();
    context.lineWidth = width;
    context.strokeStyle = color;
    context.stroke();
}

/******************** label ****************/

function MousePos(event, _canvas = canvas) {
    //event.preventDefault();
    event = (event ? event : window.event);
    return {
        x: event.pageX - _canvas.offsetLeft,
        y: event.pageY - _canvas.offsetTop
    }
}

var labelStage = null;
var labelStatus = false; // 0: no, 1: draw;
var rectifyType = 0;
var rectifyIdx = -1;
var labelLineWidth = 15;
var labelLineColor = '#f00';
const labelRectifyWidth = 4;
const cursors = ['default', 'n-resize', 'e-resize', 's-resize', 'w-resize', 'move'];

function Box(sx = 0, sy = 0, ex = 0, ey = 0) {
    this.sx = sx;
    this.sy = sy;
    this.ex = ex;
    this.ey = ey;
}
Box.prototype.clone = function () {
    return new Box(this.sx, this.sy, this.ex, this.ey);
}
Box.prototype.cloneFrom = function(_box) {
    this.sx = _box.sx;
    this.sy = _box.sy;
    this.ex = _box.ex;
    this.ey = _box.ey;
}
Box.prototype.type = 'Box';
Box.prototype.draw = function (rectify = false) {
    var posx = Math.min(this.sx, this.ex);
    var posy = Math.min(this.sy, this.ey);
    var boxw = Math.abs(this.sx - this.ex);
    var boxh = Math.abs(this.sy - this.ey);
    drawRect(ctx, posx, posy, boxw, boxh, labelLineColor, null, labelLineWidth);
    console.log('linecolor:', labelLineColor);
    if (rectify) {
        ctx.save();
        ctx.setLineDash([5, 10]);
        drawRect(ctx, posx, posy, boxw, boxh, '#fff', null, labelRectifyWidth);
        ctx.restore();
    }
}
Box.prototype.normalize = function (ix, iy, iw, ih) {
    var box = new Box(
        (this.sx - ix) / iw,
        (this.sy - iy) / ih,
        (this.ex - ix) / iw,
        (this.ey - iy) / ih,
    );
    return box;
}
Box.prototype.unnormalize = function (ix, iy, iw, ih) {
    var box = new Box(
        this.sx * iw + ix,
        this.sy * ih + iy,
        this.ex * iw + ix,
        this.ey * ih + iy,
    )
    return box;
}
Box.prototype.distance = function(x, y, returnIndex=false) {
    // the order of pd is the same as margin in css.
    var pds = [
        (x > this.sx && x < this.ex) ? Math.abs(this.sy - y) : labelLineWidth,
        (y > this.sy && y < this.ey) ? Math.abs(this.ex - x) : labelLineWidth,
        (x > this.sx && x < this.ex) ? Math.abs(this.ey - y) : labelLineWidth,
        (y > this.sy && y < this.ey) ? Math.abs(this.sx - x) : labelLineWidth
    ];
    var minval = Math.min(...pds);
    var mindex = pds.indexOf(minval);
    if(returnIndex) return [mindex, minval];
    else return minval;
}
Box.prototype.nearby = function (x, y) {
    var dist = this.distance(x, y, true);
    var mindex = dist[0], minval = dist[1];
    if (minval < labelLineWidth) return mindex + 1;
    else return 0;
}

function Point(x = 0, y = 0) {
    this.x = x;
    this.y = y;
}
Point.prototype.clone = function () {
    return new Point(this.x, this.y);
}
Point.prototype.cloneFrom = function (_point) {
    this.x = _point.x, this.y = _point.y;
}
Point.prototype.type = 'Point';
Point.prototype.draw = function (rectify = false) {
    drawPoint(ctx, this.x, this.y, labelLineColor, labelLineWidth);
    if (rectify) {
        ctx.save();
        drawPoint(ctx, this.x, this.y, '#fff', labelRectifyWidth);
        ctx.restore();
    }
}
Point.prototype.normalize = function (ix, iy, iw, ih) {
    var point = new Point(
        (this.x - ix) / iw,
        (this.y - iy) / ih
    )
    return point;
}
Point.prototype.unnormalize = function (ix, iy, iw, ih) {
    var point = new Point(
        this.x * iw + ix,
        this.y * ih + iy
    );
    return point;
}
Point.prototype.distance = function(x, y) {
    var x2 = (x - this.x) * (x - this.x);
    var y2 = (y - this.y) * (y - this.y);
    return Math.sqrt(x2 + y2)
}
Point.prototype.nearby = function (x, y) {
    var dis = this.distance(x, y);
    return dis < labelLineWidth ? 5 : 0;
}

curLabelForm = null;

/******************** dras stack ****************/

function DrawStack(_stack = null) {
    this.stack = new Array();
    if (_stack != null) {
        for (var i = 0; i < _stack.length; i++) {
            var _label = _stack[i];
            if(_label.sx == undefined) {
                this.stack.push(new Point(_label.x, _label.y));
            } else {
                this.stack.push(new Box(_label.sx, _label.sy, _label.ex, _label.ey));
            }
        }
    }
}
DrawStack.prototype.stackType = 'draw';
DrawStack.prototype.length = function() {
    return this.stack.length;
}
DrawStack.prototype.clone = function () {
    return new DrawStack(this.stack);
}
DrawStack.prototype.pushStack = function (painter) {
    var temp;
    if (painter.type[0] == 'B') {
        if (painter.sx > painter.ex) {
            temp = painter.sx;
            painter.sx = painter.ex;
            painter.ex = temp;
        }
        if (painter.sy > painter.ey) {
            temp = painter.sy;
            painter.sy = painter.ey;
            painter.ey = temp;
        }
    }
    var npainter = painter.normalize(...imgStatus.sizePara());
    this.stack.push(npainter);
}
DrawStack.prototype.popStack = function () {
    this.stack.pop();
}
DrawStack.prototype.remove = function(idx) {
    if(idx >= 0 && idx < this.length()) {
        this.stack.splice(idx, 1);
    }
}
DrawStack.prototype.insert = function(idx, label) {
    if(idx >= 0 && idx <= this.length()) {
        var nlabel = label.normalize(...imgStatus.sizePara());
        this.stack.splice(idx, 0, nlabel);
    }
}
DrawStack.prototype.label = function(idx, unnormalize=false) {
    var _label = (idx >= 0 && idx < this.length()) ? this.stack[idx] : undefined;
    if(_label != undefined && unnormalize) {
        _label = _label.unnormalize(...imgStatus.sizePara())
    }
    return _label;
}
DrawStack.prototype.topStack = function () {
    return this.label(this.length() - 1);
}
DrawStack.prototype.runStack = function () {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    imgStatus.draw();
    for (var i = 0; i < this.length(); i++) {
        var painter = this.label(i);
        var npainter = painter.unnormalize(...imgStatus.sizePara());
        npainter.draw();
    }
    $('.left h3').text("Number: " + this.length());
}
DrawStack.prototype.nearby = function (x, y) {
    var idx = -1, dis = labelLineWidth;
    for(var i = 0; i < this.length(); i++) {
        var _label = this.label(i).unnormalize(...imgStatus.sizePara());
        var thisDis = _label.distance(x, y);
        if(thisDis < dis) {
            idx = i, dis = thisDis;
        }
    }
    return idx;
}

var drawStack = new DrawStack(drawStackDict);

/****************** draw *****************/

function runDraw() {
    if (labelStage == 'label') {
        labelOperation();
    } else if (labelStage == 'rectify') {
        if(curLabelForm != null) {
            curLabelForm = drawStack.label(rectifyIdx, true);
        }
        rectifyOperation();
    } else {
        console.log("run");
        drawStack.runStack();
    }
}

window.onload = function () {
    loadImage();
    drawGrid();

    setInterval(function() {
        save();
    }, 20 * 1000);
};