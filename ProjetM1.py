import numpy as np
import matplotlib.pyplot as plt
import os
from flask import Flask, render_template, request, redirect, url_for
from sklearn.linear_model import LinearRegression
from werkzeug.utils import secure_filename

# cmd = set FLASK_APP=ProjetM1
# set FLASK_ENV=development
# flask run

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = 'static/csv'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result/', methods=['GET', 'POST'])
def result():
    #Suppression des anciens résultats
    if os.path.exists("static/csv/csvPoints.csv"):
        os.remove("static/csv/csvPoints.csv")
    if os.path.exists("static/images/linear_regression.png"):
        os.remove("static/images/linear_regression.png")

    if request.method == 'POST':

        #Sauvegarde du csv avec un nom statique + vérification de l'extension
        f = request.files['csvPoints']
        if f and allowed_file(f.filename):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename('csvPoints.csv'))) #secure_filename(f.filename)



        data = request.form
        #Construction des listes X et Y
        maximumX = 0
        i = 0
        x = []
        y = []
        for key,value in data.items():
            if i % 2 == 0:
                x.append([value])
                value = float(value)
                if value > maximumX:
                    maximumX = value
            else:
                y.append([value])
            i+= 1

        x = np.array(x,dtype=float)
        y = np.array(y,dtype=float)

        # create a linear regression model
        model = LinearRegression()
        model.fit(x, y)

        # predict y from the data
        x_new = np.linspace(0, maximumX, 100)
        y_new = model.predict(x_new[:, np.newaxis])

        # plot the results
        plt.figure(figsize=(8, 6))
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