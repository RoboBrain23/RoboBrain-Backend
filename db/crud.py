from sqlalchemy.orm import Session
import db.schemas as schemas, db.models as models
from fastapi import HTTPException, status, Depends

# * here we create our CRUD functions that will be used in our routers


# * Create a function that will store the data in the database when POST request is sent to the route


# @param db: Session ==> this is the database session that we will use to store the data in the database
# @param data: schemas.ChairData ==> this is the data that we will store in the database
def store_chair_data(db: Session, data: schemas.ReadChairData):
    # * Create a new instance of ChairData model to store the data in the database
    new_data = models.ChairData(**data.dict())
    # * Get the patient from the database using the patient_id that we got from the request body
    # * this patient will be used to create the relationship between the patient and the chair data
    patient = (
        db.query(models.Patient).filter(data.patient_id == models.Patient.id).first()
    )
    # * Create the relationship between the patient and the chair data
    new_data.patient = patient

    # * Add the new data to the database session and commit the changes to the database
    db.add(new_data)
    db.commit()
    db.refresh(new_data)

    return new_data


# * Create a fucntion that will return the last chair data for a specific patient


# @param patient_id: int ==> this is the id of the patient that we will use to get the last chair data for him
# @param db: Session ==> this is the database session that we will use to get the data from the database
def get_chair_data(patient_id: int, db: Session):
    db_data = (
        db.query(models.ChairData)
        .filter(models.ChairData.patient_id == patient_id)
        .order_by(models.ChairData.id.desc())
        .first()
    )

    # * Check if the data is None and if it is raise an HTTPException with status code 404 and a message
    if db_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data not found"
        )
    return db_data


# * Create a function that will store the patient in the database when POST request is sent to the route
# @param db: Session ==> this is the database session that we will use to store the data in the database
# @param patient: schemas.Patient ==> this is the patient that we will store in the database
def signup(db: Session, patient: schemas.SignUp):
    # * Check if the email is already exist in the database
    db_email = (
        db.query(models.Patient).filter(models.Patient.email == patient.email).first()
    )

    # * if the email is already exist raise an HTTPException with status code 400 and a message
    if db_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already exist",
        )

    # * Check the username is already exist in the database
    db_username = (
        db.query(models.Patient)
        .filter(models.Patient.username == patient.username)
        .first()
    )

    # * if the username is already exist raise an HTTPException with status code 400 and a message
    if db_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already exist",
        )

    # * Create a new instance of Patient model to store the patient in the database

    patient.id = int(patient.id)
    patient.age = int(patient.age)

    new_patient = models.Patient(**patient.dict())

    # * Add the new patient to the database session and commit the changes to the database
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


active_user = 0


# TODO: Complete patient_info CRUD function
def patient_info():
    pass


# TODO: Complete login CRUD function
def login(db: Session, patient: schemas.Login):
    db_emial = (
        db.query(models.Patient).filter(models.Patient.email == patient.email).first()
    )
    db_password = (
        db.query(models.Patient)
        .filter(models.Patient.password == patient.password)
        .first()
    )

    if (db_emial is not None) and (db_password is not None):
        active_user = db_emial.id
        return "Success"

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email or password"
    )
