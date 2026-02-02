from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import session
from schemas import Todo as TodoSchema, TodoCreate, TodoUpdate
from database import SessionLocal, Base, engine
from models import Todo

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/todos", response_model=list[TodoSchema])
def read_todos(db: session=Depends(get_db)):
    todos=db.query(Todo).all()
    return todos

@app.get("/todos/{todo_id}", response_model=TodoSchema)
def read_todo(todo_id: int, db: session=Depends(get_db)):
    db_todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@app.post("/todos", response_model=TodoSchema)
def create(todo: TodoCreate, db: session=Depends(get_db)):
    db_todo=Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/delete/{todo_id}")
def delete(todo_id: int, db: session=Depends(get_db)):
    db_todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if db_todo is None:
        return {"error": "Todo not found"}
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.patch("/todos/update/{todo_id}", response_model=TodoSchema)
def update(todo_id: int, todo: TodoUpdate, db: session=Depends(get_db)):
    db_todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if db_todo is None:
        return {"error": "Todo not found"}
    db_todo.title=todo.title if todo.title is not None else db_todo.title
    db_todo.description=todo.description if todo.description is not None else db_todo.description
    db_todo.completed=todo.completed if todo.completed is not None else db_todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

