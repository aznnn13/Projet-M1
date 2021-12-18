import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from sklearn.linear_model import LinearRegression
from werkzeug.utils import secure_filename

# Windows
# set FLASK_APP=ProjetM1
# set FLASK_ENV=development
# flask run

# Mac
# export FLASK_APP=ProjetM1.py
# export FLASK_ENV=development


# App config
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = 'static/csv'
app.secret_key = 'super secret key'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/result/', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        # Convertion de 'ImmutableMultiDict' en 'dict'
        data = request.form.to_dict()

        # On récupère l'option choisie et on l'enlève au dict
        Option = int(data.pop('Option', None))

        if Option <= 2:

            # Suppression des anciens résultats
            if os.path.exists("static/csv/csvPoints.csv"):
                os.remove("static/csv/csvPoints.csv")
            if os.path.exists("static/images/linear_regression.png"):
                os.remove("static/images/linear_regression.png")

            # Déclaration des tableaux X et Y pour la régression linéaire
            x = []
            y = []
            maximumX = 0

            if Option == 1:  # Import .csv

                # Sauvegarde du csv avec un nom statique + vérification de l'extension
                f = request.files['csvPoints']
                if f and allowed_file(f.filename):
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                        secure_filename('csvPoints.csv')))  # secure_filename(f.filename)
                else:
                    flash('Erreur: Choisir un fichier .csv', 'danger')
                    return redirect(url_for('index'))

                # Read the csv file
                df = pd.read_csv("static/csv/csvPoints.csv", sep=',')[['X', 'Y']]
                for (colname, colval) in df.iteritems():
                    if colname == 'X':
                        for value in colval.values:
                            x.append([value])
                            if value > maximumX:
                                maximumX = value

                    if colname == 'Y':
                        for value in colval.values:
                            y.append([value])

            if Option == 2:  # Ajout des points à la main

                # check if the post request has the file part
                i = 0
                for key, value in data.items():
                    if i % 2 == 0:
                        x.append([value])
                        value = float(value)
                        if value > maximumX:
                            maximumX = value
                    else:
                        y.append([value])
                    i += 1

            # Construction des listes X et Y
            x = np.array(x, dtype=float)
            y = np.array(y, dtype=float)

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

        else:  # Nouveau formulaire

            # Convertion des valeurs du dict en float
            data = dict((k, float(v)) for k, v in data.items())

            maxValue = max(data.values())
            return render_template("result.html", Option=Option, maxValue=maxValue)

        return render_template("result.html", Option=Option)


if __name__ == '__main__':
    app.run(debug=True)
