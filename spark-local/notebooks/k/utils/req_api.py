from fastapi import FastAPI, Depends, Path, HTTPException
from sqlalchemy.orm import Session
# from models import models, database
app = FastAPI()

@app.get(path="/api/v1/users/{user_id}")
def get_place(
        place_id: int):
        # , db: Session = Depends(get_db)):
    # result = db.query(Request_Inventory)#.filter(Request_Inventory.id == user_id).first()

    if result is None:
        raise HTTPException(status_code=404, detail="ID에 해당하는 User가 없습니다.")

    return {
        "status": "OK",
        "data": place_id
    }