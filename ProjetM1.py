from flask import Flask,render_template,request,redirect
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Powershell = $env:FLASK_APP = "ProjetM1"
# cmd = set FLASK_APP=ProjetM1
# flask run

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result/', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        data = request.form

        #Construction des listes X et Y
        i = 0
        x = []
        y = []
        for key,value in data.items():
            if i % 2 == 0:
                x.append([value])
            else:
                y.append([value])
            i+= 1

        x = np.array(x,dtype=float)
        y = np.array(y,dtype=float)

        # create a linear regression model
        model = LinearRegression()
        model.fit(x, y)

        # predict y from the data
        x_new = np.linspace(0, 30, 100)
        y_new = model.predict(x_new[:, np.newaxis])

        # plot the results
        plt.figure(figsize=(4, 3))
        ax = plt.axes()
        ax.scatter(x, y)
        ax.plot(x_new, y_new)

        ax.set_xlabel('x')
        ax.set_ylabel('y')

        ax.axis('tight')
        plt.savefig('static/images/linear_regression.png')
        return render_template("result.html")


if __name__ == '__main__':
    app.run(debug=True)