from pydantic import BaseModel
from datetime import date
from typing import List, Optional


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

class JadwalDokterCreate(JadwalDokterBase):
    pass

class JadwalDokter(JadwalDokterBase):
    id_jadwal_dokter: int

    class Config:
        orm_mode = True


# Janji Temu
class JanjiTemuBase(BaseModel):
    kode_janji_temu: str
    tgl_janji_temu: str
    id_dokter: int
    id_user: int
    is_relasi: bool
    id_relasi: int
    biaya_janji_temu: int

class JanjiTemuCreate(JanjiTemuBase):
    pass

class JanjiTemu(JanjiTemuBase):
    id_janji_temu: int

    class Config:
        orm_mode = True


# Janji Temu as Orang Lain
class JanjiTemuAsOrangLainBase(BaseModel):
    kode_janji_temu_as_orang_lain: str
    tgl_janji_temu_as_orang_lain: str
    id_dokter: int
    id_user: int
    biaya_janji_temu_as_orang_lain: int
    nama_lengkap_orang_lain: str
    no_bpjs_orang_lain: str
    tgl_lahir_orang_lain: str
    gender_orang_lain: str
    no_telp_orang_lain: str
    alamat_orang_lain: str

class JanjiTemuAsOrangLainCreate(JanjiTemuAsOrangLainBase):
    pass

class JanjiTemuAsOrangLain(JanjiTemuAsOrangLainBase):
    id_janji_temu_as_orang_lain: int

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

class ObatCreate(ObatBase):
    pass

class Obat(ObatBase):
    id_obat: int

    class Config:
        orm_mode = True


# Poli
class PoliBase(BaseModel):
    nama_poli: str

class PoliCreate(PoliBase):
    pass

class Poli(PoliBase):
    id_poli: int

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

# Token
class Token(BaseModel):
    access_token: str
    token_type: str
