import time
import turtle
import winsound

# Window properties
win = turtle.Screen()
win.title('Pong')
win.bgcolor('black')
win.setup(width=800,height=600)
win.tracer(0)


border_up = 285
border_left = 380

def drawField():
    # Dwaw the border around the field
    draw = turtle.Turtle()
    draw.speed(0)
    draw.color('white')
    # around the field
    draw.penup()
    
    draw.goto(-border_left, border_up)
    draw.pendown()
    draw.goto(border_left, border_up)
    draw.goto(border_left, -border_up)
    draw.goto(-border_left, -border_up)
    draw.goto(-border_left, border_up)
    draw.penup()
    # middle line
    draw.goto(0, border_up)
    draw.pendown()
    draw.goto(0, -border_up)
	
    
    draw.hideturtle()


drawField()

# Scores
scoreA = 0
scoreB = 0

# Paddle A
padA = turtle.Turtle()
padA.speed(0)
padA.shape('square')
padA.shapesize(stretch_wid=6,stretch_len=1)
padA.color('white')
padA.penup()
padA.goto(-(border_left-10),0)

# Paddle B
padB = turtle.Turtle()
padB.speed(0)
padB.shape('square')
padB.shapesize(stretch_wid=6,stretch_len=1)
padB.color('white')
padB.penup()
padB.goto(border_left-10,0)

# Ball
ball = turtle.Turtle()
ball.speed(0)
ball.shape('circle')
ball.color('white')
ball.penup()
ball.goto(0,0)

ball.dx = 0.1
ball.dy = 0.1


# Pen
pen = turtle.Turtle()
pen.speed(0)
pen.color('white')
pen.penup()
pen.hideturtle()
pen.goto(0,250)



# Functions :
def padA_up():
	y = padA.ycor()
	y += 25
	padA.sety(y)

def padA_down():
	y = padA.ycor()
	y -= 25
	padA.sety(y)

def padB_up():
	y = padB.ycor()
	y += 25
	padB.sety(y)

def padB_down():
	y = padB.ycor()
	y -= 25
	padB.sety(y)


def write():
	pen.write(f"Player A : {scoreA}    Player B : {scoreB}",align='center',font=('Courier',24,'normal'))


# Keyboard bindings
win.listen()
win.onkeypress(padA_up,'w')
win.onkeypress(padA_down,'s')
win.onkeypress(padB_up,'Up')
win.onkeypress(padB_down,'Down')

write()

# * ------------------------------------------------------------ *

# Main game loop
try:
	while True:
		win.update()

		# Moving the ball
		ball.setx(ball.xcor() + ball.dx)
		ball.sety(ball.ycor() + ball.dy)

		# Border collison
		if ball.ycor() > border_up - 10:
			ball.dy *= -1

		if ball.ycor() < -(border_up - 10):
			ball.dy *= -1

		if ball.xcor() > border_left:
			ball.setx(-100)
			ball.dx *= -1
			scoreA += 1
			pen.clear()
			write()

		if ball.xcor() < -border_left:
			ball.setx(-100)
			ball.dx *= -1
			scoreB += 1
			pen.clear()
			write()

		# Paddle and ball collision
		if (ball.xcor() > (border_left-30) and ball.xcor() < border_left-20) and (ball.ycor() < padB.ycor() + 50 and ball.ycor() > padB.ycor() - 50):
			ball.setx(border_left-30)
			ball.dx *= -1
		if (ball.xcor() < -(border_left-30) and ball.xcor() >-(border_left-20)) and (ball.ycor() < padA.ycor() + 50 and ball.ycor() > padA.ycor() - 50):
      
			ball.setx(-(border_left-30))
			ball.dx *= -1


except Exception as e:
	pass