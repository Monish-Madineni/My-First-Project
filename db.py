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
with engine.connect() as conn:
    result = conn.execute(text("select * from colleges"))
    result_dicts=[]
    for row in result.all():
        result_dicts.append(dict(row._mapping))

def search_results(include_filters,exclude_filters):
    query = "SELECT * FROM colleges "
    params = {}
    for i in include_filters:
        if include_filters.index(i)==0:
            x=i.split('|')
            query=query+'where '+x[0]+' = '+"'"+x[1]+"'"
        else:
            x=i.split('|')
            query=query+' and '+x[0]+' = '+"'"+x[1]+"'"
    
    if len(exclude_filters)!=0:
        for i in exclude_filters:
            if include_filters.index('i')==0 and len(include_filters)==0:
                x=i.split('|')
                query=query+'where '+x[0]+' != '+"'"+x[1]+"'"
            else:
                x=i.split('|')
                query=query+' and '+x[0]+' != '+"'"+x[1]+"'"

    with engine.connect() as conn:
        result = conn.execute(text("query"))
        result_dicts=[]
        for row in result.all():
            result_dicts.append(dict(row._mapping))
        return result_dicts