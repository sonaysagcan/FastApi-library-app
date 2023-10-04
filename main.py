from fastapi import FastAPI, HTTPException
from models import Base,User, Book, UpdateUserData,AddBookData
from connections import SessionLocal, engine
from datetime import datetime, timedelta
import logging

#app
app = FastAPI()

#logging
logger = logging.getLogger()
log_handler = logging.FileHandler("fastapi.log")
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

#create table
Base.metadata.create_all(bind=engine)


# Kullanıcıları listeleme
@app.get("/users/")
async def get_users():
    try:
        db = SessionLocal()
        users = db.query(User).all()
        db.close()

        if users:
            log_message = f"get_users()"
            logger.info(log_message)
            return users

        log_message = f"get_users() -> Henüz kullanıcı tanımlanmamış"
        logger.warning(log_message)
        return {"status_code":204, "detail":"Henüz kullanıcı tanımlanmamış"}

    except Exception as e:
        log_message  = f"get_users() -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


# Kullanıcıları listeleme
@app.get("/user/{user_id}")
async def get_user(user_id):
    try:
        db = SessionLocal()
        users = db.query(User).filter(User.id==user_id).first()
        db.close()
        if users:
            log_message = f"get_user() -> user_id:{user_id}"
            logger.info(log_message)
            return users

        log_message = f"get_user() -> user_id:{user_id} -> kullanıcı bulunamadı"
        logger.warning(log_message)
        return {"status_code":204, "detail":"Kullanıcı bulunamadı"}

    except Exception as e:
        log_message  = f"get_user() -> user_id{user_id} -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


# Kullanıcı güncelleme
@app.put("/user/{user_id}")
async def update_user(user_id: int, user_data: UpdateUserData):
    try:
        db = SessionLocal()
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            for key, value in user_data.model_dump().items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            db.close()

            log_message = f"update_user() -> user_id:{user_id}"
            logger.info(log_message)
            return {"status_code":201,"message": f"{user_id} id nolu kullanıcı güncellendi"}

        db.close()
        log_message = f"update_user() -> user_id:{user_id} -> kullanıcı bulunamadı"
        logger.warning(log_message)
        return {"status_code": 204, "message": f"{user_id} id nolu kullanıcı bulunamadı"}

    except Exception as e:
        log_message = f"update_user() -> user_id{user_id} -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")

@app.put("/user/add/")
async def add_user(user_data: UpdateUserData):
    try:
        db = SessionLocal()
        new_user = User(**user_data.dict())  # Kullanıcıyı oluştururken kwargs kullanarak tüm veriler alıınıyor
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        log_message = f"add_user()"
        logger.info(log_message)
        return {"status_code":201,"message": "Kullanıcı başarıyla eklendi"}

    except Exception as e:
        log_message = f"add_user() -> user_data:{user_data} -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


# Kullanıcı silme
@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    try:
        db = SessionLocal()
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            db.close()
            log_message = f"delete_user() -> user_id:{user_id}"
            logger.info(log_message)
            return {"message": "Kullanıcı silindi"}
        db.close()

        log_message = f"delete_user() -> user_id:{user_id} -> kullanıcı bulunamadı"
        logger.warning(log_message)
        return {"status_code": 204, "message": f"{user_id} id nolu kullanıcı bulunamadı"}

    except Exception as e:
        log_message = f"delete_user() -> user_id:{user_id} -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


#yeni kitap girişi
@app.put("/book/add/")
async def add_book(book_data: AddBookData):
    try:
        db = SessionLocal()
        new_book = Book(**book_data.dict())  # kwargs kullanarak tüm veriler alıınıyor
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        db.close()
        log_message = f"add_book()"
        logger.info(log_message)
        return {"status_code":201,"message": "Kitap başarıyla eklendi"}

    except Exception as e:
        log_message = f"add_book() -> book_data:{book_data} -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")

# Kitap alma
@app.post("/users/{user_id}/books/{book_id}")
async def borrow_book(user_id: int, book_id: int, max_reading_time: int = 7):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        book = db.query(Book).filter(Book.id == book_id).first()

        if user and book:
            if book.owner_id is None:
                book.owner_id = user_id
                due_date = datetime.now() + timedelta(days=max_reading_time)  # Kullanıcıya süre girilmezse max 1 hafta
                book.due_date = due_date
                db.commit()
                db.close()
                return {"message": "Kitap alındı", "due_date": due_date}
            else:
                db.close()
                return {"status_code": 204, "message": "Kitap başkası tarafından ödünç alınmış"}
        db.close()
        return {"status_code": 204, "message": f"Kullanıcı veya kitap bulunamadı"}

    except Exception as e:
        log_message = f"borrow_book() -> user_id:{user_id} -> book_id:{book_id} -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


# Kitap iade etme
@app.post("/users/{user_id}/books/{book_id}/return")
async def return_book(user_id: int, book_id: int):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        book = db.query(Book).filter(Book.id == book_id).first()

        if user and book:
            if book.owner_id == user_id:
                book.owner_id = None
                book.due_date = None
                db.commit()
                db.close()

                log_message = f"return_book() -> user_id:{user_id} book_id:{book_id}"
                logger.info(log_message)
                return {"status_code":201,"message": "Kitap iade edildi"}

            else:
                db.close()
                log_message = f"return_book() -> user_id:{user_id} book_id:{book_id} message-> Bu kitap sizin değil"
                logger.warning(log_message)
                return {"status_code": 204, "message": "Bu kitap sizin değil"}

        db.close()
        return {"status_code": 204, "message": "Kullanıcı veya kitap bulunamadı"}

    except Exception as e:
        log_message = f"return_book() -> user_id:{user_id} -> book_id:{book_id} -> {e} "
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


# Verilen kitapları listeleme
@app.get("/books/provided/")
async def list_provided_books():
    try:
        db = SessionLocal()
        returned_books = db.query(Book).filter(Book.owner_id.isnot(None)).all()
        db.close()

        log_message = f"list_provided_books()"
        logger.info(log_message)
        if len(returned_books) > 0:
            return returned_books
        log_message = f"list_provided_books() -> Dışarıda kitap bulunamadı"
        logger.warning(log_message)
        return {"status_code": 204, "message": "Dışarıda kitap bulunamadı"}

    except Exception as e:
        log_message = f"list_provided_books() -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")


# Gecikmiş kitapları listeleme
@app.get("/books/overdue/")
async def list_overdue_books():
    try:
        db = SessionLocal()
        overdue_books = db.query(Book).filter(Book.due_date < datetime.now()).all()
        db.close()

        log_message = f"list_overdue_books()"
        logger.info(log_message)

        if len(overdue_books) > 0:
            return overdue_books

        log_message = f"list_overdue_books() -> Zamanı geçmiş kitap bulunamadı"
        logger.warning(log_message)
        return {"status_code": 204, "message": "Zamanı geçmiş kitap bulunamadı"}

    except Exception as e:
        log_message = f"list_overdue_books() -> {e}"
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu")
