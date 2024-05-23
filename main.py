# package: fastapi, bcrypt, sqlalchemy, python-jose

# test lokal uvicorn main:app --host 0.0.0.0 --port 8000 --reload --


# kalau deploy di server: pip install gunicorn
# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --daemon
# mematikan gunicorn (saat mau update):
# ps ax|grep gunicorn 
# pkill gunicorn


from os import path
from fastapi import Depends, Request, FastAPI, HTTPException

from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from pydantic import BaseModel

from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
models.BaseDB.metadata.create_all(bind=engine)

import jwt
import datetime

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


app = FastAPI(title="Web service Sehatyuk",
    version="0.0.1",)

app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#hapus ini kalau salt sudah digenerate
# @app.get("/getsalt")
# async def getsalt():
#     hasil = bcrypt.gensalt()
#     return {"message": hasil}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def root():
    return {"message": "Dokumentasi API: [url]:8000/docs"}

# nanti disembunyikan, untuk iniisasi tambah user dan items, biar nggak manual setiap db diganti
# hati2 ini menghapus data di tabel item dan user
# @app.put("/init")
# async def init(db: Session = Depends(get_db)):
#     crud.delete_all_item(db)
#     crud.delete_all_user(db)
#     u = schemas.UserCreate
#     u.username = "default"
#     u.password = "ilkomupi"
#     crud.create_user(db,u)
    
#     i = schemas.ItemCreate
#     i.title = "Mie Bakso"
#     i.description = "Mie Bakso gurih dengan bakso yang besar"
#     i.img_name = "bakso.png"
#     i.price = 12000
#     crud.create_item(db,i)

#     i = schemas.ItemCreate
#     i.title = "Nasi Goreng"
#     i.description = "Nasi goreng enak dan melimpahr"
#     i.img_name = "nasi_goreng.png"
#     i.price = 10000
#     crud.create_item(db,i)

#     i = schemas.ItemCreate
#     i.title = "Nasi Kuning"
#     i.description = "Nasi kuning lezat pisan"
#     i.img_name = "nasi_kuning.png"
#     i.price = 17000
#     crud.create_item(db,i)

#     i = schemas.ItemCreate
#     i.title = "Kupat Tahu"
#     i.description = "Kupat Tahu dengan kuah melimpah"
#     i.img_name = "kupat_tahu.png"
#     i.price = 5000
#     crud.create_item(db,i)

#     i = schemas.ItemCreate
#     i.title = "Pecel Lele"
#     i.description = "Pecel lele dengan ikan lele yang segar"
#     i.img_name = "pecel_lele.png"
#     i.price = 11000
#     crud.create_item(db,i)

#     i = schemas.ItemCreate
#     i.title = "Ayam Geprek"
#     i.description = "Pecel lele dengan ikan lele yang segar"
#     i.img_name = "ayam_geprek.png"
#     i.price = 11000
#     crud.create_item(db,i)

#     return {"message": "OK"}


# create user 
@app.post("/create_user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_email = crud.get_user_by_email(db, email=user.email_user)
    db_user_no_telp = crud.get_user_by_no_telp(db, no_telp=user.no_telp_user)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Error: Email sudah digunakan")
    elif db_user_no_telp:
        raise HTTPException(status_code=400, detail="Error: No telp sudah digunakan")

    return crud.create_user(db=db, user=user)


# hasil adalah akses token    
@app.post("/login_email") #,response_model=schemas.Token
async def login_email(user: schemas.UserLoginEmail, db: Session = Depends(get_db)):
    if not authenticate_by_email(db,user):
        raise HTTPException(status_code=400, detail="Username atau password tidak cocok")

    # ambil informasi username
    user_login = crud.get_user_by_email(db,user.email_user)
    if user_login:
        access_token  = create_access_token(user.email_user)
        user_id = user_login.id_user
        return {"user_id":user_id,"access_token": access_token}
    else:
        raise HTTPException(status_code=400, detail="User tidak ditemukan, kontak admin")
    
@app.post("/login_no_telp") #,response_model=schemas.Token
async def login_no_telp(user: schemas.UserLoginPhone, db: Session = Depends(get_db)):
    if not authenticate_by_no_telp(db,user):
        raise HTTPException(status_code=400, detail="Username atau password tidak cocok")

    # ambil informasi username
    user_login = crud.get_user_by_no_telp(db,user.no_telp_user)
    if user_login:
        access_token  = create_access_token(user.no_telp_user)
        user_id = user_login.id_user
        return {"user_id":user_id,"access_token": access_token}
    else:
        raise HTTPException(status_code=400, detail="User tidak ditemukan, kontak admin")


# # untuk debug saja, nanti rolenya admin?
# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme) ):
#     usr =  verify_token(token)
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users

# #lihat detil user_id
@app.get("/get_user_by_id/{id_user}", response_model=schemas.User)
def read_user(id_user: int, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) 
    db_user = crud.get_user(db, id_user=id_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# tambah item ke keranjang
# response ada id (cart), sedangkan untuk paramater input  tidak ada id (cartbase)
@app.post("/create_relasi/", response_model=schemas.Relasi ) # response_model=schemas.Cart 
def create_relasi(
    relasi: schemas.RelasiCreate, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    return crud.create_relasi(db=db, relasi=relasi)

# untuk semua isi cart, hanya untuk debug
# @app.get("/carts/", response_model=list[schemas.Cart])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
#     carts = crud.get_carts(db, skip=skip, limit=limit)
#     return carts

#ambil semua relasi milik user
@app.get("/get_relasi/{id_user}", response_model=list[schemas.Relasi])
def read_relasi(id_user:int, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    relasi = crud.get_relasi(db, id_user=id_user)
    return relasi

#ambil isi cart milik seorang user
@app.get("/get_relasi_by_id/{id_relasi}", response_model=schemas.Relasi)
def read_relasi(id_relasi:int, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    relasi = crud.get_relasi_by_id(db, id_relasi=id_relasi)
    return relasi

# # hapus item cart berdasarkan cart id
@app.delete("/delete_relasi/{id_relasi}")
def delete_relasi(id_relasi:int,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme) ):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    return crud.delete_relasi_by_id(db,id_relasi)

@app.post("/create_dokter/", response_model=schemas.Dokter ) # response_model=schemas.Cart 
def create_dokter(
    dokter: schemas.DokterCreate, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    return crud.create_dokter(db=db, dokter=dokter)

#ambil semua dokter
@app.get("/get_dokter/", response_model=list[schemas.Dokter])
def read_dokter(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    dokter = crud.get_dokter(db, skip, limit)
    return dokter


#ambil isi dokter milik seorang user
@app.get("/get_dokter_by_id/{id_dokter}", response_model=schemas.Dokter)
def read_dokter(id_dokter:int, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    dokter = crud.get_dokter_by_id(db, id_dokter=id_dokter)
    return dokter

# # hapus item dokter berdasarkan dokter id
@app.delete("/delete_dokter/{id_dokter}")
def delete_dokter(id_dokter:int,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme) ):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    return crud.delete_dokter_by_id(db,id_dokter)

# obat
@app.post("/create_obat/", response_model=schemas.Obat ) # response_model=schemas.Cart 
def create_obat(
    obat: schemas.ObatCreate, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    return crud.create_obat(db=db, obat=obat)

#ambil semua obat
@app.get("/get_obat/", response_model=list[schemas.Obat])
def read_obat(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    obat = crud.get_obat(db, skip, limit)
    return obat

#ambil isi obat milik seorang user
@app.get("/get_obat_by_id/{id_obat}", response_model=schemas.Obat)
def read_obat(id_obat:int, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    obat = crud.get_obat_by_id(db, id_obat=id_obat)
    return obat

# # hapus item obat berdasarkan obat id
@app.delete("/delete_obat/{id_obat}")
def delete_obat(id_obat:int,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme) ):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    return crud.delete_obat_by_id(db,id_obat)

#ambil semua jadwal dokter
@app.get("/get_jadwal_dokter/", response_model=list[schemas.JadwalDokter])
def read_jadwal_dokter(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    jadwal_dokter = crud.get_jadwal_dokter(db, skip, limit)
    return jadwal_dokter

#ambil semua jadwal dokter berdasarkan id
@app.get("/get_jadwal_dokter_by_id/{id_dokter}", response_model=list[schemas.JadwalDokter])
def read_jadwal_dokter(id_dokter:int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    jadwal_dokter = crud.get_jadwal_dokter_by_id(db, id_dokter=id_dokter)
    return jadwal_dokter

@app.post("/create_janji_temu/", response_model=schemas.JanjiTemu ) # response_model=schemas.Cart 
def create_janji_temu(
    janji_temu: schemas.JanjiTemuCreate, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
    # print(usr)
    return crud.create_janji_temu(db=db, janji_temu=janji_temu)

# # hapus item cart berdasarkan user id
# @app.delete("/clear_whole_carts_by_userid/{user_id}")
# def delete_item_user_cart(user_id:int,db: Session = Depends(get_db),token: str = Depends(oauth2_scheme) ):
#     usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
#     return crud.delete_cart_by_userid(db,user_id=user_id)


# #### ITEMS

# # create item, tapi hanya untuk internal, role terpisah? nanti saja kalau sempat
# # kalau sudah selsai disembunyikan agar mhs tdk menambah item random
# # @app.post("/items/", response_model=schemas.ItemBase)
# # def create_item(item: schemas.ItemBase, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
# #     usr =  verify_token(token)
# #     return crud.create_item(db=db, item=item)

# # semua item
# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     usr =  verify_token(token)
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items

# image dokter berdasarkan id
path_img = "image/"
@app.get("/dokter_image/{id_dokter}")
def read_image(id_dokter:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token)
    dokter = crud.get_dokter_by_id(db,id_dokter)
    if not(dokter):
        raise HTTPException(status_code=404, detail="id tidak valid")
    nama_image =  dokter.foto_dokter
    if not(path.exists(path_img + "cariDokterPage/" + nama_image)):
        raise HTTPException(status_code=404, detail="File dengan nama tersebut tidak ditemukan")
    
    fr =  FileResponse(path_img + "cariDokterPage/" + nama_image)
    return fr
   
@app.get("/user_image/{id_user}")
def read_image(id_user:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token)
    user = crud.get_user(db,id_user)
    if not(user):
        raise HTTPException(status_code=404, detail="id tidak valid")
    nama_image =  user.foto_user
    if not(path.exists(path_img + "profilePage/" + nama_image)):
        raise HTTPException(status_code=404, detail="File dengan nama tersebut tidak ditemukan")
    
    fr =  FileResponse(path_img + "profilePage/" + nama_image)
    return fr   
   
@app.get("/relasi_image/{id_relasi}")
def read_image(id_relasi:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token)
    relasi = crud.get_relasi_by_id(db,id_relasi)
    if not(relasi):
        raise HTTPException(status_code=404, detail="id tidak valid")
    nama_image =  relasi.foto_relasi
    if not(path.exists(path_img + "relasiPage/" + nama_image)):
        raise HTTPException(status_code=404, detail="File dengan nama tersebut tidak ditemukan")
    
    fr =  FileResponse(path_img + "relasiPage/" + nama_image)
    return fr   
   
@app.get("/obat_image/{id_obat}")
def read_image(id_obat:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    usr =  verify_token(token)
    obat = crud.get_obat_by_id(db,id_obat)
    if not(obat):
        raise HTTPException(status_code=404, detail="id tidak valid")
    nama_image =  obat.foto_obat
    if not(path.exists(path_img + "cariObatPage/" + nama_image)):
        raise HTTPException(status_code=404, detail="File dengan nama tersebut tidak ditemukan")
    
    fr =  FileResponse(path_img + "cariObatPage/" + nama_image)
    return fr   

# # cari item berdasarkan deskripsi
# @app.get("/search_items/{keyword}")
# def cari_item(keyword:str,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     usr =  verify_token(token)

#     return crud.get_item_by_keyword(db,keyword)

# ###################  status

# #status diset manual dulu karena cukup rumit kalau ditangani constraitnya

# #keranjang terisi --> user checkout dan siap bayar
# @app.post("/set_status_harap_bayar/{user_id}")
# def set_status_harap_bayar(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     return crud.insert_status(db=db,user_id=user_id,status="belum_bayar")

# #user membayar
# @app.post("/pembayaran/{user_id}")
# def bayar(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     return crud.pembayaran(db=db,user_id=user_id)


# #user sudah bayar --> penjual menerima 
# @app.post("/set_status_penjual_terima/{user_id}")
# def set_status_penjual_terima(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     return crud.insert_status(db=db,user_id=user_id,status="pesanan_diterima")

# # user sudah bayar --> penjual menolak
# # isi keranjang dikosongkan
# @app.post("/set_status_penjual_tolak/{user_id}")
# def set_status_penjual_terima(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     # isi cart dikosongkan
#     crud.delete_cart_by_userid(db,user_id=user_id)
#     return crud.insert_status(db=db,user_id=user_id,status="pesanan_ditolak")


# # penjual menerima --> pesanan diantar
# @app.post("/set_status_diantar/{user_id}")
# def set_status_penjual_terima(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     return crud.insert_status(db=db,user_id=user_id,status="pesanaan_diantar")


# # pesanan diantar -->pesanan diterima
# @app.post("/set_status_diterima/{user_id}")
# def set_status_penjual_terima(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     #cart dikosongkan
#     #idealnya isi cart dipindahkan ke transaksi untuk arsip transaksi
#     crud.delete_cart_by_userid(db,user_id=user_id)
#     return crud.insert_status(db=db,user_id=user_id,status="pesanan_selesai")


# @app.get("/get_status/{user_id}")
# def last_status(user_id:int,  db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
#     usr =  verify_token(token) #bisa digunakan untuk mengecek apakah user cocok (tdk boleh akses data user lain)
#     return crud.get_last_status(db,user_id)


# ######################## AUTH

# # periksa apakah username ada dan passwordnya cocok
# # return boolean TRUE jika username dan password cocok
def authenticate_by_email(db,user: schemas.UserCreate):
    user_cari = crud.get_user_by_email(db=db, email=user.email_user)
    if user_cari:
        # print(user.email_user)
        # print(user.password_user)
        print(f'{user_cari.password_user} {crud.hashPassword(user.password_user)}')
        return (user_cari.password_user == crud.hashPassword(user.password_user))
    else:
        return False  
      
def authenticate_by_no_telp(db,user: schemas.UserCreate):
    user_cari = crud.get_user_by_no_telp(db=db, no_telp=user.no_telp_user)
    if user_cari:
        return (user_cari.password_user == crud.hashPassword(user.password_user))
    else:
        return False    
    

SECRET_KEY = "sehatyukgaissss"


def create_access_token(email):
    # info yang penting adalah berapa lama waktu expire
    expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)    # .now(datetime.UTC)
    access_token = jwt.encode({"email":email,"exp":expiration_time},SECRET_KEY,algorithm="HS256")
    return access_token    


def verify_token(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=["HS256"])  # bukan algorithm,  algorithms (set)
        email = payload["email"]  
     
    # exception jika token invalid
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Unauthorize token, expired signature, harap login")
    except jwt.PyJWKError:
        raise HTTPException(status_code=401, detail="Unauthorize token, JWS Error")
    # except jwt.JWTClaimsError:
    #     raise HTTPException(status_code=401, detail="Unauthorize token, JWT Claim Error")
    # except jwt.JWTError:
    #     raise HTTPException(status_code=401, detail="Unauthorize token, JWT Error")   
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorize token, unknown error"+str(e))
    
    return {"email": email}



    
# internal untuk testing, jangan dipanggil langsung
# untuk swagger  .../doc supaya bisa auth dengan tombol gembok di kanan atas
# kalau penggunaan standard, gunakan /login

@app.post("/token", response_model=schemas.Token)
async def token(req: Request, form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):

    f = schemas.UserCreate
    f.email_user = form_data.username
    f.password_user = form_data.password
    if not authenticate_by_email(db,f):
        raise HTTPException(status_code=400, detail="email or password tidak cocok")

    #info = crud.get_user_by_email_user(form_data.email_user)
    # email = info["email"]   
    # role  = info["role"]   
    email_user  = form_data.username

    #buat access token\
    # def create_access_token(user_name,email,role,nama,status,kode_dosen,unit):
    access_token  = create_access_token(email_user)

    return {"access_token": access_token, "token_type": "bearer"}
