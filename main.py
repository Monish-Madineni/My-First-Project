from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Request,Form
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from rapidfuzz import fuzz, process
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

course_types=["CSE", "ECE", "EEE", "MEC", "CIV", "INF", "CSM", "CSD", "CSO", "CSC", "CSA", "CSB", "CSG", "CSN", "AIM", "AI", "AID", "CSW", "ECM", "ECI", "EIE", "CHE", "MET", "CME", "MIN", "MTE", "MCT", "MMS", "BME", "BSE", "AGR", "BIO", "PHE", "AUT", "ANE", "DRG", "EVL", "CIC", "CIC", "FDT", "DTD", "PLG", "GEO", "TEX"]
caste_types=["OC","BC_A","BC_B","BC_C","BC_D","BC_E","ST","SC","EWS"]
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/search/")
def homepage(request: Request):

    return templates.TemplateResponse(
        request,
        "search.html",
        {
            "request": request,
            "course_types": course_types,
            "caste_types": caste_types,
            "results": []
        }
    )

@app.get("/smart_search/")
def homepage(request: Request):

    return templates.TemplateResponse(
        request,
        "smartsearch.html",
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
class Courses_LastRank(SQLModel, table=True):
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
class Courses_phase1(SQLModel, table=True):
    __tablename__='courses_phase1'
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
class Courses_phase2(SQLModel, table=True):
    __tablename__='courses_phase2'
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

def college_suggestion_items(session: Session, search_text: str, limit: int = 6):
    normalized_search = search_text.strip()
    if not normalized_search:
        return []

    colleges = session.exec(select(Colleges)).all()
    choices = {
        f"{college.inst_code or ''} {college.inst_name or ''}".strip(): college
        for college in colleges
    }

    direct_matches = [
        college for college in colleges
        if normalized_search.casefold() in (college.inst_code or "").casefold()
        or normalized_search.casefold() in (college.inst_name or "").casefold()
    ]
    fuzzy_matches = [
        choices[match_text]
        for match_text, score, _ in process.extract(
            normalized_search,
            choices.keys(),
            scorer=fuzz.WRatio,
            limit=limit * 3
        )
        if score >= 55
    ]

    suggestions = []
    seen_codes = set()
    for college in direct_matches + fuzzy_matches:
        if not college.inst_code or college.inst_code in seen_codes:
            continue
        seen_codes.add(college.inst_code)
        suggestions.append({
            "inst_code": college.inst_code,
            "inst_name": college.inst_name,
            "url": f"/colleges/{college.inst_code}"
        })
        if len(suggestions) == limit:
            break
    return suggestions

@app.get("/college_suggestions")
def college_suggestions(session: SessionDep, q: str = Query("")):
    return {"results": college_suggestion_items(session, q)}

@app.get("/college_search")
def college_search(session: SessionDep, q: str = Query("")):
    search_text = q.strip()
    if not search_text:
        return RedirectResponse(url="/", status_code=303)

    suggestions = college_suggestion_items(session, search_text, limit=1)
    if suggestions:
        return RedirectResponse(url=suggestions[0]["url"], status_code=303)

    return RedirectResponse(url="/search/", status_code=303)

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
    gender: str| None=None
    phase: int| None=None

def db_querying(session: Session, filters: CollegeFilter):
    if filters.phase==1:
        course_table=Courses_phase1
    elif filters.phase==2:
        course_table=Courses_phase2
    else:
        course_table=Courses_LastRank

    statement=(select(Colleges,course_table).join(course_table,Colleges.inst_code==course_table.inst_code))

    if filters.caste:
        caste_type=filters.caste
    else:
        caste_type="ocb"

    caste_column=getattr(course_table,caste_type)

    if filters.upper_rank==112345678:
        safe_statement = statement.where(caste_column < filters.lower_rank).order_by(caste_column.desc()).limit(5)
        safe_results = session.exec(safe_statement).all()
        results=session.exec(statement).all()

        safe_results.reverse()

        normal_statement = statement.where(caste_column >= filters.lower_rank)

        if filters.upper_rank is not None:
            normal_statement = normal_statement.where(caste_column <= filters.upper_rank)

        normal_statement = normal_statement.order_by(caste_column.asc())
        normal_results = session.exec(normal_statement).all()

        results = safe_results + normal_results

        response=[]
        
        for college, course in results:
            response.append({
                "college": college.inst_name,
                "course": course.branch_name,
                "last_rank": getattr(course,caste_type),
                "inst_code": college.inst_code
            })
        return response
    else:

        # COURSE FILTERS
        if filters.lower_rank==None:
            filters.lower_rank=0
        if filters.upper_rank==None:
            filters.upper_rank=10000

        if filters.courses:
            statement=statement.where(course_table.branch_code.in_(filters.courses))

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
        statement = statement.order_by(caste_column.asc())

        results=session.exec(statement).all()
        response = []

        
        for college, course in results:
            response.append({
                "college": college.inst_name,
                "course": course.branch_name,
                "last_rank": getattr(course,caste_type),
                "inst_code": college.inst_code
            })
        return response
@app.get("/")
def homepage(request: Request ):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request}
    )

@app.post("/search_results")
def read_colleges( session: SessionDep,request: Request,courses: list[str] = Form(None),caste: str = Form(None),lower_rank: int = Form(None),upper_rank: int = Form(None),gender: str=Form(None),phase: int = Form(None)):
    caste=caste or "OC"
    gender=gender or "BOYS"
    lower_rank=lower_rank or 0
    upper_rank=upper_rank or 10000
    courses=courses or ["CSE"]
    phase=phase or 3
    filters = CollegeFilter(
        courses=courses,
        caste=(caste+gender[0]).lower(),
        lower_rank=lower_rank,
        upper_rank=upper_rank,
        phase=phase
    )

    response=db_querying(session,filters)

    return templates.TemplateResponse(
        request,
        "search.html",
        {"request": request, "course_types": course_types, "caste_types": caste_types,"selected_courses":courses,"selected_caste":caste,"selected_gender":gender,"selected_lowerrank":lower_rank,"selected_upperrank":upper_rank,"selected_phase":phase, "results": response }
    )

@app.post("/smart_search_results")
def read_colleges( session: SessionDep,request: Request,courses: list[str] = Form(None),caste: str = Form(None),user_rank: int = Form(None),gender: str=Form(None),phase: int = Form(None)):
    caste=caste or "OC"
    gender=gender or "BOYS"
    user_rank=user_rank or 0
    courses=courses or ["CSE"]
    phase=phase or 3
    filters = CollegeFilter(
        courses=courses,
        caste=(caste+gender[0]).lower(),
        lower_rank=user_rank,
        upper_rank=112345678,
        phase=phase
    )

    response=db_querying(session,filters)

    return templates.TemplateResponse(
        request,
        "smartsearch.html",
        {"request": request, "course_types": course_types, "caste_types": caste_types,"selected_courses":courses,"selected_caste":caste,"selected_gender":gender,"selected_userrank":user_rank,"selected_phase":phase, "results": response }
    )

@app.get("/colleges/{inst_code}")
def particular_college(session:SessionDep, request: Request, inst_code, phase: int = 3):
    if phase == 1:
        course_table = Courses_phase1
    elif phase == 2:
        course_table = Courses_phase2
    else:
        course_table = Courses_LastRank

    statement = (select(Colleges, course_table)
                 .join(course_table, Colleges.inst_code == course_table.inst_code))
    statement = statement.where(Colleges.inst_code == inst_code)
    results = session.exec(statement).all()

    college = results[0][0] if results else None

    return templates.TemplateResponse(
        request,
        "college.html",
        {
            "request": request,
            "results": results,
            "selected_phase": phase,
            "college": college
        }
    )
    

@app.get("/api/colleges/")
def api_read_colleges( session: SessionDep, filters: CollegeFilter):
    
    response=db_querying(session,filters)

    return {"count":len(response),"results":response}