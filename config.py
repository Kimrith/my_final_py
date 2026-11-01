class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "super-secret-key"

    # Bakong KHQR Payment Configuration
    BAKONG_ID = "chey_kimrith@bkrt"
    BAKONG_MERCHANT_NAME = "KIMCHEY_Eco"
    BAKONG_MERCHANT_CITY = "Phnom Penh"
    BAKONG_ACQUIRING_ID = "chey_kimrith@bkrt"
    BAKONG_API_BASE_URL = "https://api-bakong.nbc.gov.kh"
    BAKONG_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiMDM3NjZmOWE1NDM2NDYyNyJ9LCJpYXQiOjE3OTMxMTY3NzEsImV4cCI6MTgwMDg5Mjc3MX0.GJlaxxqXD6A_h9-wAQKb9iAUbgz4x6a4i0GEZ-6V5Pg"