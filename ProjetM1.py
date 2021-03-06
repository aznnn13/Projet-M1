import json
import os
import pickle

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flaskext.mysql import MySQL
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from werkzeug.utils import secure_filename

from flask_session import Session

# Windows
# set FLASK_APP=ProjetM1
# set FLASK_ENV=development
# flask run

# Mac
# export FLASK_APP=ProjetM1.py && export FLASK_ENV=development && flask run


# App config
app = Flask(__name__, static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
ALLOWED_EXTENSIONS = {'csv'}
app.secret_key = 'super secret key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Matplotlib cfg
matplotlib.use('agg')
matplotlib.pyplot.switch_backend('Agg')

# DB config
mysql = MySQL()
if app.config['ENV'] == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')
mysql.init_app(app)
mysql = MySQL(app)

# Admin session config
adminUsername = "admin"
adminPassword = "projetm1"


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

        # On recupere l'option choisie et on l'enleve au dict
        Option = int(data.pop('Option', None))

        if Option <= 2:

            # Suppression des anciens resultats
            if os.path.exists("upload/csv/csvPoints.csv"):
                os.remove("upload/csv/csvPoints.csv")
            if os.path.exists("static/images/linear_regression.png"):
                os.remove("static/images/linear_regression.png")

            # Declaration des tableaux X et Y pour la regression lineaire
            x = []
            y = []
            maximumX = 0

            if Option == 1:  # Import .csv

                # Sauvegarde du csv avec un nom statique + verification de l'extension
                f = request.files['csvPoints']
                if f and allowed_file(f.filename):
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                        secure_filename('csvPoints.csv')))  # secure_filename(f.filename)
                else:
                    flash('Erreur: Choisir un fichier .csv', 'danger')
                    return redirect(url_for('index'))

                # Read the csv file
                df = pd.read_csv("upload/csv/csvPoints.csv", sep=',')[['X', 'Y']]
                for (colname, colval) in df.iteritems():
                    if colname == 'X':
                        for value in colval.values:
                            x.append([value])
                            if value > maximumX:
                                maximumX = value

                    if colname == 'Y':
                        for value in colval.values:
                            y.append([value])

            if Option == 2:  # Ajout des points a la main

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

            saveData = data.pop('saveData', None)

            # Convertion des valeurs du dict en float
            data = dict((k, float(v)) for k, v in data.items())

            if saveData == "on":
                # Champs de la table user
                Param1 = str(data.get('Param1', 0))
                Param2 = str(data.get('Param2', 0))
                Param3 = str(data.get('Param3', 0))
                Param4 = str(data.get('Param4', 0))
                Param5 = str(data.get('Param5', 0))

                # Requete
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO `user` (`id`, `Param1`, `Param2`, `Param3`, `Param4`, `Param5`) "
                    "VALUES (NULL, " + Param1 + "," + Param2 + "," + Param3 + ", " + Param4 + ", " + Param5 + ")")
                conn.commit()
                cursor.close()

            maxValue = max(data.values())

            return render_template("result.html", Option=Option, maxValue=maxValue)

        return render_template("result.html", Option=Option)


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def adminDashboard():
    # Si on est deja connecte
    if 'isAdmin' in session:
        return render_template("admin/dashboard.html")
    else:
        data = request.form
        usernameInput = data.get('Username')
        passwordInput = data.get('Password')

        if passwordInput == adminPassword and usernameInput == adminUsername:
            session["isAdmin"] = 1
            return render_template("admin/dashboard.html")
        else:
            flash('Erreur: Mot de passe incorrect', 'danger')
            return redirect(url_for('index'))


@app.route('/admin/deconnexion')
def deconnexion():
    session.pop('isAdmin')
    return redirect(url_for('index'))


@app.route('/admin/export')
def adminExport():
    return render_template("admin/export.html")


@app.route('/export_bdd')
def export_bdd():
    # Suppression de l'ancien export
    if os.path.exists("upload/csv/export.csv"):
        os.remove("upload/csv/export.csv")

    # Requete
    conn = mysql.connect()
    cursor = conn.cursor()
    user = pd.read_sql('SELECT * FROM user', conn)
    user.to_csv('upload/csv/export.csv', index=False)

    path = "upload/csv/export.csv"
    return send_file(path, as_attachment=True)


# ------------------- API ------------------------

@app.route('/apiRegression', methods=['POST'])
def apiRegression():
    if request.method == 'POST':
        # Suppression des anciens r??sultats
        if os.path.exists("static/images/linear_regression.png"):
            os.remove("static/images/linear_regression.png")

        jsonPoints = request.data
        json_dictionary = json.loads(jsonPoints)
        x = []
        y = []
        maximumX = 0

        for v in json_dictionary['x']:
            x.append([v])
            if float(v) > maximumX:
                maximumX = float(v)

        for v in json_dictionary['y']:
            y.append([v])

        print("Liste X :" + str(x))
        print("Liste Y :" + str(y))

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
        # return send_from_directory('static/images', 'linear_regression.png')
        return "Ok"


@app.route('/apiFormulaire', methods=['POST'])
def apiFormulaire():
    jsonFormulaire = request.data
    json_dictionary = json.loads(jsonFormulaire)

    listParameters = list((float(v)) for v in json_dictionary['parameters'])

    if json_dictionary['saveData'] == "true":
        # Requete
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO `user` (`id`, `Param1`, `Param2`, `Param3`, `Param4`, `Param5`) "
            "VALUES (NULL, " + str(listParameters[0]) + "," + str(listParameters[1]) + "," +
            str(listParameters[2]) + ", " + str(listParameters[3]) + ", " +
            str(listParameters[4]) + ")")
        conn.commit()
        cursor.close()

    # load the model from disk
    filename = 'model/recidive_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

    prediction = [listParameters[0], listParameters[1], listParameters[2], listParameters[3], listParameters[4]]

    # changing input data to a numpy array
    input_data_as_numpy_array = np.asarray(prediction)

    # reshape the numpy array
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)

    # standardize the data
    scaler = preprocessing.StandardScaler()
    std_data = scaler.fit_transform(input_data_reshaped)

    # Predict the input's class
    svm_prediction = loaded_model.predict(std_data)

    # Return prediction
    return str(svm_prediction[0])


if __name__ == '__main__':
    app.run(debug=True)
