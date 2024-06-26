from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional, Literal
from enum import Enum

class ResponseMSG(BaseModel):
    msg: str

# Poli
class PoliBase(BaseModel):
    nama_poli: str

class PoliCreate(PoliBase):
    pass

class Poli(PoliBase):
    id_poli: int

    class Config:
        orm_mode = True

# Dokter
class DokterBase(BaseModel):
    nama_lengkap_dokter: str
    spesialisasi_dokter: str
    lama_pengalaman_dokter: int
    alumnus_dokter: str
    harga_dokter: int
    minat_klinis_dokter: str
    foto_dokter: str
    rating_dokter: float
    id_poli: int
    poli: Optional[Poli] = []

class DokterCreate(DokterBase):
    pass

class Dokter(DokterBase):
    id_dokter: int

    class Config:
        orm_mode = True


# Jadwal Dokter
class JadwalDokterBase(BaseModel):
    id_dokter: int
    tanggal_jadwal_dokter: date
    is_full: int
    start_time: time
    end_time: time

class JadwalDokterCreate(JadwalDokterBase):
    pass

class JadwalDokter(JadwalDokterBase):
    id_jadwal_dokter: int

    class Config:
        orm_mode = True

# Jenis Obat
class JenisObatBase(BaseModel):
    jenis_obat: str

class JenisObatCreate(JenisObatBase):
    pass

class JenisObat(JenisObatBase):
    id_jenis_obat: int

    class Config:
        orm_mode = True


# Obat
class ObatBase(BaseModel):
    nama_obat: str
    deskripsi_obat: str
    komposisi_obat: str
    dosis_obat: str
    peringatan_obat: str
    efek_samping_obat: str
    foto_obat: str
    id_jenis_obat: int
    jenis_obat: Optional[JenisObat] = []

class ObatCreate(ObatBase):
    pass

class Obat(ObatBase):
    id_obat: int

    class Config:
        orm_mode = True



# Relasi
class RelasiBase(BaseModel):
    id_user: int
    nama_lengkap_relasi: str
    no_bpjs_relasi: str
    tgl_lahir_relasi: date
    gender_relasi: str
    no_telp_relasi: str
    alamat_relasi: str
    foto_relasi: str
    tipe_relasi: str

class RelasiCreate(RelasiBase):
    pass

class Relasi(RelasiBase):
    id_relasi: int

    class Config:
        orm_mode = True


# Review
class ReviewBase(BaseModel):
    id_user: int
    id_dokter: int
    rating: int
    review_content: Optional[str]

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id_review: int

    class Config:
        orm_mode = True

# User
class UserBase(BaseModel):
    nama_lengkap_user: str
    tgl_lahir_user: date
    gender_user: str
    alamat_user: str
    no_bpjs_user: str
    no_telp_user: str
    email_user: str
    foto_user: str

class UserCreate(UserBase):
    password_user: str

class UserLoginEmail(BaseModel):
    email_user: str
    password_user: str

class UserLoginPhone(BaseModel):
    no_telp_user: str
    password_user: str

class User(UserBase):
    id_user: int

    class Config:
        orm_mode = True

class Password(BaseModel):
    old_password: str
    new_password: str

# Janji Temu as Orang Lain
class JanjiTemuAsOrangLainBase(BaseModel):
    nama_lengkap_orang_lain: str
    no_bpjs_orang_lain: str
    tgl_lahir_orang_lain: date
    gender_orang_lain: str
    no_telp_orang_lain: str
    alamat_orang_lain: str

class JanjiTemuAsOrangLainCreate(JanjiTemuAsOrangLainBase):
    pass

class JanjiTemuAsOrangLain(JanjiTemuAsOrangLainBase):
    id_janji_temu_as_orang_lain: int

    class Config:
        orm_mode = True

class StatusEnum(str, Enum):
    MENUNGGU_AMBIL_ANTRIAN = 'Menunggu Ambil Antrian'
    MENUNGGU_ANTRIAN = 'Menunggu Antrian'
    DALAM_SESI = 'Dalam Sesi'
    MENUNGGU_PEMBAYARAN = 'Menunggu Pembayaran'
    SELESAI = 'Selesai'

# Janji Temu
class JanjiTemuBase(BaseModel):
    kode_janji_temu: str
    tgl_janji_temu: date
    id_dokter: int
    id_user: int
    is_relasi: int
    id_relasi: int
    biaya_janji_temu: int
    id_janji_temu_as_orang_lain: int
    status: StatusEnum
    dokter: Optional[Dokter] = []
    user: Optional[User] = []
    relasi: Optional[Relasi] = []
    janji_temu_as_orang_lain: Optional[JanjiTemuAsOrangLain] = []

class JanjiTemuCreate(JanjiTemuBase):
    pass

class JanjiTemu(JanjiTemuBase):
    id_janji_temu: int

    class Config:
        orm_mode = True


# Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Pengingat Minum Obat
class PengingatMinumObatBase(BaseModel):
    id_obat: int
    id_user: int
    dosis: int
    sendok: str
    jadwal: str
    aturan: str
    obat: Optional[Obat] = []
    user: Optional[User] = [] 
    # nama_obat: Optional[Obat] = []
    # foto_obat: Optional[Obat] = []
    # detail_obat: Optional[Obat] = []

class PengingatMinumObatCreate(PengingatMinumObatBase):
    pass

class PengingatMinumObat(PengingatMinumObatBase):
    id_pengingat: int
    # obat: Optional[Obat] = []

    class Config:
        orm_mode = True
        
        
# rekam medis
class RekamMedisBase(BaseModel):
    id_janji_temu: int
    id_obat: int
    hasil_diagnosis: str
    pengobatan: str
    dosis_obat: str
    catatan: str
    janji_temu: Optional[JanjiTemu] = []
    obat: Optional[Obat] = []
    
class RekamMedis(RekamMedisBase):
    id_rekam_medis: int

    class Config:
        orm_mode = True