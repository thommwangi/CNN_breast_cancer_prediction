import os
from flask import Flask
from application import *
import psycopg2
app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('postgres://gxepbisjfrjtec:4def25d675d77b6c635d4f87148cbce6dde33f7f9fa3c0c903627de4b70ee6ab@ec2-54-162-207-150.compute-1.amazonaws.com:5432/d4o12uqtk4ajej')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:froyo95*@127.0.0.1/mammodb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#DATABASE_URL = os.environ['postgres://gxepbisjfrjtec:4def25d675d77b6c635d4f87148cbce6dde33f7f9fa3c0c903627de4b70ee6ab@ec2-54-162-207-150.compute-1.amazonaws.com:5432/d4o12uqtk4ajej']

#conn = psycopg2.connect(DATABASE_URL, sslmode='require')
db.init_app(app)

def main():
    db.create_all() 

if __name__ == "__main__":
    with app.app_context():
        main()