from flask import Flask, render_template
from sqlalchemy import create_engine,text
engine = create_engine(
    "mysql+pymysql://root:2006@localhost/college_details?charset=utf8mb4"
)
app=Flask(__name__)
from sqlalchemy import create_engine,text
engine = create_engine(
    "mysql+pymysql://root:2006@localhost/college_details?charset=utf8mb4"
)
def load_collegetypes_from_db_colleges():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'colleges' order by column_name"))
        tempctypes=[]
        for row in result.all():
            tempctypes.extend(dict(row._mapping).values())
        tempctypes.remove('inst_code')
        tempctypes.remove('inst_name')
        tempctypes.remove('nos')
        ctypes=dict()
        for i in tempctypes:
            result = conn.execute(text('select distinct '+i+' from colleges order by '+i ))
            x=[]
            for row in result.all():
                x.extend(dict(row._mapping).values())
            ctypes[i]=x
            x=[]
        return ctypes
def load_colunm_names_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT  from colleges"))
        columns=[]
        for row in result.all():
            columns.append(dict(row._mapping))
    return columns
@app.route("/")
def hello():
    collegetypes=load_collegetypes_from_db_colleges()
    return render_template('browse1.html',FT=collegetypes)
if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)