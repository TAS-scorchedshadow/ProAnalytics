from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)
app.secret_key = "super secret"
bootstrap = Bootstrap(app)

array_shots = [[150,0]]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/target')
def target():
    p = figure(plot_width=1500, plot_height=1500)
    c1 = p.quad(top=[600], bottom=[-600], left=[-600], right=[600], color="black").glyph
    c1.line_color = "white"
    c1.line_width = 4
    c2 = p.circle([0], [0], size=600, color="black").glyph
    c2.line_color = "white"
    c2.line_width = 4
    c3 = p.circle([0], [0], size=420, color="black").glyph
    c3.line_color = "white"
    c3.line_width = 4
    c4 = p.circle([0], [0], size=280, color="black").glyph
    c4.line_color = "white"
    c4.line_width = 4
    c5 = p.circle([0], [0], size=140, color="black").glyph
    c5.line_color = "white"
    c5.line_width = 4
    c6 = p.circle([0], [0], size=70, color="black").glyph
    c6.line_color = "white"
    c6.line_width = 4
    c6 = p.circle([100], [0], size=35, color="black").glyph
    c6.line_color = "white"
    c6.line_width = 2
    for shots in range(len(array_shots)):
        print(array_shots[0])
        c7 = p.circle([array_shots[0][0]], [array_shots[0][1]], size=15, color="red").glyph
        c7.line_color = "white"
        c7.line_width = 2
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    plotShot(p, 0, 5, 1)
    script, div = components(p)
    return render_template('target.html', script=script, div=div)


def plotShot(p, x, y, num):K
    p.circle([x], [y], size=30, color="black", line_color="white", line_width=2)
    p.text([x],[y], text=[str(num)], text_baseline="middle", text_align="center", color="white")

if __name__ == '__main__':
    app.run()
