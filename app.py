from flask import Flask, render_template,request
from db import load_collegetypes_from_db_colleges,search_results
app=Flask(__name__)
from sqlalchemy import create_engine,text
engine = create_engine(
    "mysql+pymysql://root:2006@localhost/college_details?charset=utf8mb4"
)
@app.route("/")
def hello():
    collegetypes=load_collegetypes_from_db_colleges()
    return render_template('browse1.html',FT=collegetypes)



@app.route("/search", methods=["POST"])

def search():
    filters = request.form.getlist("filters")  # e.g. ["Girls:1", "Coed:2", "Hostel:0"]
    
    include_filters = []
    exclude_filters = []
    
    for f in filters:
        name, state = f.split(":")
        if state == "1":
            include_filters.append(name)   # must have
        elif state == "2":
            exclude_filters.append(name)   # must NOT have
    
    # Example: build query
    query = "SELECT * FROM colleges "
    params = {}
    include_filters.sort()
    exclude_filters.sort()
    for i in include_filters:
        x=i.split('|')
        if include_filters.index(i)==0:
            query=query+'where '+'('+x[0]+' = '+"'"+x[1]+"'"
            prev_type=x[0]
        elif prev_type==x[0]:
            query=query+' or '+x[0]+' = '+"'"+x[1]+"'"
        else:
            query=query+')' +'and' +'('+x[0]+' = '+"'"+x[1]+"'"
            prev_type==x[0]
        if include_filters.index(i)==len(include_filters)-1:
            query=query+')'
    
    if len(exclude_filters)!=0:
        for i in exclude_filters:
            x=i.split('|')
            if len(include_filters)==0:
                query=query+'where '+x[0]+' != '+"'"+x[1]+"'"
                prev_type=x[0]
            elif exclude_filters.index(i)==0:
                query=query+' and '+x[0]+' != '+"'"+x[1]+"'"
                prev_type==x[0]
            elif prev_type==x[0]:
                query=query+' or '+x[0]+' != '+"'"+x[1]+"'"
            else:
                query=query+' and '+x[0]+' != '+"'"+x[1]+"'"
                prev_type=x[0]
    print(include_filters)
    print(exclude_filters)
    print(query)

    with engine.connect() as conn:
        result = conn.execute(text(query))
        result_dicts=[]
        for row in result.all():
            result_dicts.append(dict(row._mapping))
    return render_template('result.html',FT=result_dicts)
    
if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)