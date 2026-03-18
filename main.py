from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Request,Form
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="templates")

course_types=["CSE", "ECE", "EEE", "MEC", "CIV", "INF", "CSM", "CSD", "CSO", "CSC", "CSA", "CSB", "CSG", "CSN", "AIM", "AI", "AID", "CSW", "ECM", "ECI", "EIE", "CHE", "MET", "CME", "MIN", "MTE", "MCT", "MMS", "BME", "BSE", "AGR", "BIO", "PHE", "AUT", "ANE", "DRG", "EVL", "CIC", "CIC", "FDT", "DTD", "PLG", "GEO", "TEX"]
caste_types=["OC","BC_A","BC_B","BC_C","BC_D","BC_E","ST","SC","EWS"]

@app.get("/")
def homepage(request: Request):

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "course_types": course_types,
            "caste_types": caste_types,
            "results": []
        }
    )
class Colleges(SQLModel, table=True):
    __tablename__='colleges'
    inst_code: str| None= Field(default=None,primary_key=True)
    inst_name: str| None= None
    place: str| None= None
    dist_code: str| None= None
    coed: str| None= None
    type: str| None = None
    estab: str| None= None
    affiliation: str| None
class Courses(SQLModel, table=True):
    __tablename__='courses'
    inst_code: str| None = Field(default=None,primary_key=True)
    branch_code: str| None = Field(default= None,primary_key=True)
    branch_name: str| None= None
    ocb: int| None= None
    ocg: int| None= None
    bc_ab: int| None= None
    bc_ag: int| None= None
    bc_bb: int| None= None
    bc_bg: int| None= None
    bc_cb: int| None= None
    bc_cg: int| None= None
    bc_db: int| None= None
    bc_dg: int| None= None
    bc_eb: int| None= None
    bc_eg: int| None= None
    scb: int| None= None
    scg: int| None= None
    stb: int| None= None
    stg: int| None= None
    ewsb: int| None= None
    ewsg: int| None= None
    fee: int| None= None

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

class CollegeFilter(BaseModel):
    #colleges table
    include_places: list[str]| None=None
    exclude_places: list[str]| None=None
    coed: str| None=None
    include_dist_codes: list[str]| None=None
    exclude_dist_codes: list[str]| None=None
    include_college_types: list[str]| None=None
    exclude_college_types: list[str]| None=None
    
    #courses table
    caste: str| None=None
    courses: list[str]| None=None
    lower_rank: int| None= None
    upper_rank: int| None= None
    fee_lower: int| None= None
    fee_upper: int| None= None

@app.post("/colleges/")
def read_colleges( session: SessionDep,request: Request,courses: list[str] = Form(None),caste: str = Form(None),lower_rank: int = Form(None),upper_rank: int = Form(None),gender: str=Form(None)):
    filters = CollegeFilter(
        courses=courses,
        caste=(caste+gender[0]).lower(),
        lower_rank=lower_rank,
        upper_rank=upper_rank
    )
    statement=(select(Colleges,Courses).join(Courses,Colleges.inst_code==Courses.inst_code))

# COURSE FILTERS

    if filters.courses:
        statement=statement.where(Courses.branch_code.in_(filters.courses))
    
    if filters.caste:
        caste_type=filters.caste
    else:
        caste_type="ocb"
    caste_column=getattr(Courses,caste_type)
    if filters.lower_rank is not None:
        statement=statement.where(caste_column>=filters.lower_rank)
    if filters.upper_rank is not None:
        statement=statement.where(caste_column<=filters.upper_rank)
    
    #   COLLEGE FILTERS

    if filters.include_dist_codes:
        statement=statement.where(Colleges.dist_code.in_(filters.include_dist_codes))
    if filters.exclude_dist_codes:
        statement=statement.where(Colleges.dist_code.notin_(filters.exclude_dist_codes))
    if filters.include_places:
        statement=statement.where(Colleges.place.in_(filters.include_places))
    if filters.exclude_places:
        statement=statement.where(Colleges.place.notin_(filters.exclude_places))
    if filters.coed:
        statement=statement.where(Colleges.coed==filters.coed)
    if filters.include_college_types:
        statement=statement.where(Colleges.type.in_(filters.include_college_types))
    if filters.exclude_college_types:
        statement=statement.where(Colleges.type.notin_(filters.exclude_college_types))

    
    results=session.exec(statement).all()
    response = []

    
    for college, course in results:
        response.append({
            "college": college.inst_name,
            "course": course.branch_name,
            "last_rank": getattr(course,caste_type)
        })
    print(response)

    return templates.TemplateResponse(
        "search.html",
        {"request": request, "course_types": course_types, "caste_types": caste_types, "results": response }
    )