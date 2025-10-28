from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db

app = FastAPI()

# Tạo bảng (nếu chưa có)
Base.metadata.create_all(bind=engine)

@app.get("/")
def check_connection(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1;")
        return {"message": "✅ Database connected successfully!"}
    except Exception as e:
        return {"error": str(e)}
