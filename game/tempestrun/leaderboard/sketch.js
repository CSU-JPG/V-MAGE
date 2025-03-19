var scores = [
  ["ghast", 9000],
  ["a", 5],
  ["b", 6],
  ["c", 10],
  ["g", 2],
  ["x", 5],
];

var players = [];
for (let i = 0; i < scores.length; i++) {
  players[i] = { name: scores[i][0], score: scores[i][1] };
}

players.sort(function (a, b) {
  return b.score - a.score;
});

var squares = [];

function setup() {
  createCanvas(windowWidth, windowHeight);
  angleMode(DEGREES);
  for (let i = 0; i < scores.length; i++) {}
  for (let i = 0; i < scores.length; i++) {
    console.log(players[i]);
  }
  for (let i = 0; i < 30; i++) {
    squares[i] = [
      random(0, windowWidth),
      random((windowWidth * 3) / 4, windowWidth + 250),
      0,
      random(5, 10) * random([-1, 1]),
    ];
  }
}

function get_index(arr, val) {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] == val) {
      return i;
    }
  }
  return -1;
}

function draw() {
  background(220);
  strokeWeight(1);
  for (let i = 0; i < squares.length; i++) {
    push();
    translate(squares[i][0], squares[i][1]);
    rotate(squares[i][2]);
    squares[i][2] -= squares[i][3];
    squares[i][1] -= abs(squares[i][3]) * 1;
    if (squares[i][1] < -100) {
      squares[i] = [
        random(0, windowWidth),
        windowHeight + 100,
        0,
        random(5, 10) * random([-1, 1]),
      ];
    }
    rectMode(CENTER);
    fill(220);
    rect(0, 0, 75, 75);
    pop();
  }
  textAlign("center");
  textFont("consolas");
  textSize(75);
  text("Tempest Run", windowWidth / 2, 100);
  textSize(50);
  text("HighScores", windowWidth / 2, 175);
  var w = windowWidth;
  var h = windowHeight;
  strokeWeight(2);
  var text_size = 60;
  textSize((text_size * 3) / 4);
  line(w / 4, 250, (w * 3) / 4, 250);
  var y = 250 + players.length * text_size;
  line(w / 4, y, (w * 3) / 4, y);
  for (let i = 0; i < players.length; i++) {
    line(w / 4, 250 + i * text_size, (w * 3) / 4, 250 + i * text_size);
    text(
      players[i].name,
      w / 2 - w / 8,
      250 + (text_size * 3) / 4 + i * text_size
    );
    text(
      players[i].score,
      w / 2 + w / 8,
      250 + (text_size * 3) / 4 + i * text_size
    );
  }
  line(w / 4, 250, w / 4, y);
  line((w * 3) / 4, 250, (w * 3) / 4, y);
  line(w / 2, 250, w / 2, y);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}
