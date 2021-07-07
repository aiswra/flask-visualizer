from flask import Flask, render_template,request, redirect, url_for,session
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json

import pandas as pd
from sqlalchemy import *
import plotly.express as px

from flask_wtf import FlaskForm

# models and form shall be imported prior to use
from forms import *
from models import *


# from wtforms_sqlalchemy.fields import QuerySelectField
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.automap import automap_base

app = Flask(
    __name__,
    instance_relative_config=False,
    template_folder="templates",
    static_folder="static"
)

from database import init_db, engine, db_session
#import database
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

items=db_session.query(Dummy).all()
connection = engine.connect()
# census = Table('Dummy', metadata, autoload=True, autoload_with=engine)
# query = insert(census).values(index=census.count(), x=0.5, y=0.6, group="group-6")
# connection.execute(query)
# df = pd.DataFrame([(i.group, i.x, i.y) for i in items],columns=['group', 'x', 'y'])
df = pd.read_sql_table('Dummy', engine)

# write to database
@app.route("/dbinsert")
def dbinsert():
    u = User('admin3', 'admin@localhost3')
    db_session.add(u)
    db_session.commit()
    return "data added"

# read from database
@app.route("/dbread")
def dbread():
    pass_user = request.args.get('u', None)
    if(pass_user):
        user_current = User.query.filter(User.name == pass_user).first()
        return "<h1>{}</h1>".format(user_current.email)
    else:
        return "No username"

# read data via session
@app.route("/dbread_session")
def dbread_session():
    pass_user = session.get('u',None)
    if(pass_user):
        user_current = User.query.filter(User.name == pass_user).first()
        return "<h1>{}</h1>".format(user_current.email)
    else:
        return "No username"

# write to database via form
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data)
        db_session.add(user)
        db_session.commit()
        # flash('Thanks for registering')
        return redirect(url_for("regReader"))
    return render_template('reg.html', form=form)


# write to database via form
@app.route('/reg_user', methods=['GET', 'POST'])
def reg_user():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data)
        db_session.add(user)
        db_session.commit()
        session['u']=user.name
        # flash('Thanks for registering')
        return redirect(url_for("dbread",u =(user.name)))
    return render_template('reg.html', form=form)

def generateChart(group_selection='group-1'):
    # load data
    items=db_session.query(Dummy).all()
    df = pd.read_sql_table('Dummy', engine)
    # df = pd.DataFrame([(i.group, i.x, i.y) for i in items],
    #               columns=['group', 'x', 'y'])

    # Generate charts
    graphs = [ px.bar(df, x="x", y="y", color="group",barmode="group", title="Grouped Bar Chart")
    , px.bar(df[df['group']==group_selection], x="x", y="y", color="group",barmode="group", title="Single Group Bar Chart")]

    # encode plotly graphs in JSON
    return graphs

@app.route('/chartView', methods=['GET', 'POST'])
def chartView():
    # Load graphs
    graphs = generateChart(session.get('selected',None))
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    # Group selection dropdown
    form = AddItem(request.form)
    if request.method == 'POST':
        connection = engine.connect()
        census = Table('Dummy', metadata, autoload=True, autoload_with=engine)
        query = insert(census).values(index=census.count(), x=form.x.data, y=form.y.data, group=form.group.data)
        connection.execute(query)
        session['selected'] = form.group.data
        # update charts
        graphs = generateChart(session.get('selected',None))
        ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template("chartView.html", graphJSON=graphJSON, ids=ids, form=form)
        # text = form.x.data
        # return "Hello {}".format(text)
    return render_template("chartView.html", graphJSON=graphJSON, ids=ids, form=form)

@app.route('/testdb', methods=['GET', 'POST'])
def testdb():
    items=db_session.query(Dummy).all()
    connection = engine.connect()
    # census = Table('Dummy', metadata, autoload=True, autoload_with=engine)
    # query = insert(census).values(index=census.count(), x=0.5, y=0.6, group="group-6")
    # connection.execute(query)
    # df = pd.DataFrame([(i.group, i.x, i.y) for i in items],columns=['group', 'x', 'y'])
    df = pd.read_sql_table('Dummy', engine)
    # groups = df.group.unique()
    fig = px.bar(df, x="x", y="y", color="group",barmode="group", title="Single Group Bar Chart")
    # encode plotly graphs in JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # str = "all groups {}".format(groups)
    return render_template("testdb.html", graphJSON=graphJSON)


# read inserted database via form
@app.route("/regReader")
def regReader():
    return render_template('regReader.html', users=db_session.query(User).all())


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/c/Users/antho/Documents/queryselectexample/test.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/test.db'
app.config['SECRET_KEY'] = 'secret'
#
# db = SQLAlchemy(app)
# db.Model.metadata.reflect(db.engine)


# load data
# engine = create_engine('sqlite:///../data/test.db')
# df = pd.read_sql_table('Dummy', engine)
# group_choices = df['group'].unique()

# read database
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()
# Base.metadata.reflect(engine)


    # def __repr__(self):
    #     return '[UserInput {}]'.format(self.name)
# def choice_query():
#     return UserInput.query
#
# class ChoiceForm(FlaskForm):
#     opts = QuerySelectField(query_factory=choice_query, allow_blank=False, get_label='name')
#

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/project")
def project():
    return render_template("project.html")

@app.route("/project/plotly-data-visualisation")
def project_page_1():
    # create visuals
    # graphs = [
    #     {'data': [go.Bar(x=df[df['group']=="group-1"]['x'],y=df[df['group']=="group-1"]['y'], name = 'group-1'),
    #               go.Bar(x=df[df['group']=="group-2"]['x'],y=df[df['group']=="group-2"]['y'], name = 'group-2'),
    #               go.Bar(x=df[df['group']=="group-3"]['x'],y=df[df['group']=="group-3"]['y'], name = 'group-3')],
    #      'layout': {
    #             'title': 'Random Number Table',
    #             'yaxis': {'title': "y"},
    #             'xaxis': {'title': "x"},
    #             'barmode':'group'
    #      }
    #      }
    # ]
    graphs = [ px.bar(df, x="x", y="y", color="group",barmode="group", title="Grouped Bar Chart")
    , px.bar(df[df['group']=="group-1"], x="x", y="y", color="group",barmode="group", title="Single Group Bar Chart")]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("p1.html",ids=ids, graphJSON=graphJSON)

@app.route("/project/plotly-data-visualisation-interactive")
def p2():
    return render_template("p2.html", graphJSON=gm())

def gm(group_selection='group-1'):
    fig = px.bar(df[df['group']==group_selection], x="x", y="y", color="group",barmode="group", title="Single Group Bar Chart")
    # encode plotly graphs in JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))


# from wtforms import Form, BooleanField, StringField, validators
# class MyForm(Form):
#     group = SelectField(label='Group', choices=group_choices)
# @app.route('/form', methods=['GET', 'POST'])
# def p3():
#     form = ChoiceForm()
#     form.opts.query =df.group.unique()
#
#     if form.validate_on_submit():
#         return render_template("p3.html", graphJSON=gm(form.opts.data), form=form)
#     return render_template("p3.html", graphJSON=gm(), form=form)

# from wtforms import Form, BooleanField, StringField, PasswordField, validators,SelectField
# class RegistrationForm(Form):
#     username = SelectField('Username',choices=group_choices)

#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm(request.form)
#     if request.method == 'POST' and form.validate():
#         user = form.username.data
#         #db_session.add(user)
#         # flash('Thanks for registering')
#         #return "<h1>{}</h1>".format(user)
#         return render_template("register.html", graphJSON=gm(user), form=form)
#     return render_template('register.html', form=form, graphJSON=gm())



# connection = engine.connect()
# metadata = MetaData()
# census = Table('Dummy', metadata, autoload=True, autoload_with=engine)
# metadata.create_all(engine)
# query = insert(census).values(index=census.count(), x=1, y=2, group="group-4")
# ResultProxy = connection.execute(query)


# class Registration(Form):
#     username = StringField('Username', [validators.Length(min=4, max=25)])
#     email = StringField('Email Address', [validators.Length(min=6, max=35)])
#     password = PasswordField('New Password', [
#         validators.DataRequired(),
#         validators.EqualTo('confirm', message='Passwords must match')
#     ])
#     confirm = PasswordField('Repeat Password')
#     accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

@app.route('/register2', methods=['GET', 'POST'])
def register2():
    form = Registration(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')


        return "number of users {}".format(user)
    return render_template('register2.html', form=form)

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)
if __name__ == '__main__':
    main()
