
// --- CANVAS FIELD DESIGN/LOGIC ---

const canv = document.getElementById("field")
const ctx = canv.getContext("2d")

function drawPitch() {
    ctx.beginPath()

    //outline
    ctx.moveTo(20,11)
    ctx.lineTo(619,11)
    ctx.lineTo(619,409)
    ctx.lineTo(21,409)
    ctx.lineTo(21,11)

    //center line
    ctx.moveTo(320,10)
    ctx.lineTo(320,410)

    //boxes
    ctx.moveTo(20,98)
    ctx.lineTo(110,98)
    ctx.lineTo(110,322) 
    ctx.lineTo(20,322)

    ctx.moveTo(620,98)
    ctx.lineTo(530,98)
    ctx.lineTo(530,322) 
    ctx.lineTo(620,322)

    ctx.moveTo(20,156)
    ctx.lineTo(50,156)
    ctx.lineTo(50,264)
    ctx.lineTo(20,264)

    ctx.moveTo(620,156)
    ctx.lineTo(590,156)
    ctx.lineTo(590,264)
    ctx.lineTo(620,264)

    //goal
    ctx.moveTo(620, 188)
    ctx.lineTo(630, 188)
    ctx.lineTo(630, 232)
    ctx.lineTo(620, 232)

    //center point and circle
    ctx.moveTo(320,210)
    ctx.arc(320, 210, 2, 0, Math.PI*2)

    ctx.moveTo(380,210)
    ctx.arc(320, 210, 60, 0, Math.PI*2)

    //left pen spot and D
    ctx.moveTo(80,210)
    ctx.arc(80, 210, 1, 0, Math.PI*2)

    ctx.moveTo(130,210)
    ctx.arc(80, 210, 50, 0, 0.92)
    ctx.moveTo(130,210)
    ctx.arc(80, 210, 50, 0, -0.92, true)

    //right pen spot and D
    ctx.moveTo(560,210)
    ctx.arc(560, 210, 1, 0, Math.PI*2)

    ctx.moveTo(510,210)
    ctx.arc(560, 210, 50, Math.PI, Math.PI + 0.92)
    ctx.moveTo(510,210)
    ctx.arc(560, 210, 50, Math.PI, Math.PI - 0.92, true)

    //corner arcs
    ctx.moveTo(30,10)
    ctx.arc(20, 10, 10, 0, Math.PI/2)

    ctx.moveTo(620,20)
    ctx.arc(620, 10, 10, Math.PI/2, Math.PI)

    ctx.moveTo(610,410)
    ctx.arc(620, 410, 10, -Math.PI, -Math.PI/2)

    ctx.moveTo(20,400)
    ctx.arc(20, 410, 10, -Math.PI/2, 0)

    ctx.lineWidth = 2
    ctx.strokeStyle = "white"
    ctx.stroke()
}

function drawBall() {
    ctx.beginPath()
    ctx.moveTo(ballX+4, ballY)
    ctx.arc(ballX, ballY, 4, 0, Math.PI*2)
    ctx.fillStyle = 'grey'
    ctx.fill()
    ctx.strokeStyle = 'black'
    ctx.stroke()
}

//initlal drawings
let ballX = 320
let ballY = 210
drawPitch()
drawBall()

//Redraw script for click-to-place ball logic

function render() {
    ctx.clearRect(0,0, 640, 420)
    drawPitch()
    drawBall()
}


// --- CALC DISTANCE/ANGLE

const distSpan = document.getElementById("distance")
const angSpan = document.getElementById("angle")

const GOAL_X = 120
const GOAL_Y = 40
const L_POST = 44
const R_POST = 36

//convert units; UI field is 600x400, model field is 120x80
function UI_to_model(ballX, ballY) {
    new_x = (ballX-20) / 5
    new_y = (ballY-10) / 5
    return {x: new_x, y: new_y}
}

//calc distance
function distance(x, y) {
    dist = Math.sqrt( (GOAL_X - x)**2 + (GOAL_Y - y)**2 )
    distSpan.textContent = dist.toFixed(2)
    return dist
}

//calc angle
function angle(x, y) {
    const angTop = Math.atan2(L_POST - y, GOAL_X - x)
    const angBot = Math.atan2(R_POST - y, GOAL_X - x)
    let angle = ( Math.abs(angTop - angBot) ) * (180 / Math.PI)
    angSpan.textContent = angle.toFixed(1)
    return angle
}

//redraw ball on click; display new distance/angle
canv.addEventListener('click', function(event) {
    const rect = canv.getBoundingClientRect()
    //ensure click is inbounds
    if (event.clientX-rect.left >= 20 && event.clientX-rect.left <= 620 && 
        event.clientY-rect.top >= 10 && event.clientY-rect.top <= 410) 
        {

        ballX = event.clientX - rect.left
        ballY = event.clientY - rect.top

        model_coordinates = UI_to_model(ballX, ballY)

        distance(model_coordinates.x, model_coordinates.y)
        angle(model_coordinates.x, model_coordinates.y)
        render()
    }
});


// --- PREDICT VALUE

//establish payload for model

function gatherInput() {
    return {
        underPressure: document.getElementById('UnderPressure').checked,
        oneOnOne: document.getElementById('OneOnOne').checked,
        firstTime: document.getElementById('FirstTime').checked,
        shotTechnique: document.getElementById('shotTechnique').value,
        bodyPart: document.getElementById('bodyPart').value,
        shotType: document.getElementById('shotType').value
    }
}

document.getElementById('predButton').addEventListener('click', function() {
    const inputs = gatherInput()

    const payload = {
        distance: distSpan.textContent,
        angle: angSpan.textContent,
        under_pressure: inputs.underPressure ? 1 : 0,
        one_on_one: inputs.oneOnOne ? 1 : 0,
        first_time: inputs.firstTime ? 1 : 0,
        shot_technique: inputs.shotTechnique,
        body_part: inputs.bodyPart,
        shot_type: inputs.shotType
    }

    // console.log(payload)

    fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        const xG = data.xG
        // console.log('Setting xG display to:', xG)
        const xG_label = document.getElementById('xG')
        // console.log('Found element:', el)
        xG_label.textContent = xG
    })
});