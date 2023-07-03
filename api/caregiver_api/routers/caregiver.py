from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from auth.schema import Token
import db.database as database, api.caregiver_api.db.schemas as schemas, api.caregiver_api.db.crud as crud
from db.database import get_db
from db.models import Patient, CareGiver

router = APIRouter(tags=["caregiver"], prefix="/caregiver")


# Creating New CareGiver User In DB
@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    caregiver: schemas.SignUpCareGiver,
    authorize: AuthJWT = Depends(),
    db: Session = Depends(database.get_db),
):
    return crud.signup_caregiver(caregiver=caregiver, db=db, authorize=authorize)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    caregiver: schemas.Login,
    authorize: AuthJWT = Depends(),
    db: Session = Depends(database.get_db),
):
    return crud.login_caregiver(db=db, authorize=authorize, caregiver=caregiver)


@router.get("/info", response_model=schemas.CareGiverInfo, status_code=200)
async def get_info(
    authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )
    current_user = authorize.get_jwt_subject()
    return crud.caregiver_info(caregiver_id=current_user, db=db)


@router.put(
    "/update/{caregiver_id}",
    response_model=schemas.CareGiverInfo,
    status_code=status.HTTP_200_OK,
)
async def update(
    caregiver_id: int,
    caregiver: schemas.EditProfileCareGiver,
    authorize: AuthJWT = Depends(),
    db: Session = Depends(database.get_db),
):
    return crud.update_caregiver(
        db=db, authorize=authorize, caregiver_id=caregiver_id, caregiver=caregiver
    )


@router.put("/assign-patients")
async def assign_patients(
    assignment: schemas.CareGiverAssignment, db: Session = Depends(get_db)
):
    # first we need to get the the caregiver to assign this one to one or more patients
    caregiver = db.query(CareGiver).filter_by(id=assignment.caregiver_id).first()

    # Check the validation of the caregiver
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")

    # get the patient by id
    patients = db.query(Patient).filter(Patient.id.in_(assignment.patient_ids)).all()

    # make sure all the patients exist
    if len(patients) != len(assignment.patient_ids):
        raise HTTPException(status_code=404, detail="One or more patients not found")

    # assign the patients to the caregiver
    caregiver.patients = patients
    db.commit()

    return {"message": "Patients assigned successfully"}


@router.get("/assigned-patients")
def list_assigned_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    assigned_patients = []
    for patient in patients:
        for caregiver in patient.caregivers:
            assigned_patients.append(
                {
                    "caregiver_id": caregiver.id,
                    "caregiver_name": caregiver.username,
                    "patient_id": patient.id,
                    "patient_name": patient.first_name,
                }
            )

    return {"assigned_patients": assigned_patients}
