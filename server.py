from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg

app = FastAPI()

# Разрешаем сайту (даже с GitHub) присылать данные на этот сервер
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# СТРОКА ПОДКЛЮЧЕНИЯ К ПОСТГРЕСУ
# ВНИМАНИЕ: Замени 'твой_пароль_от_postgres' на пароль, который ты вводишь при входе в pgAdmin!
DB_CONNECT = "dbname=postgres user=postgres password=Askhab2008Q. host=db.tmfrlplagzucokufdsvf.supabase.co port=5432"

class UserProfile(BaseModel):
    tg_id: int
    username: str
    display_name: str
    game: str
    rank: str
    voice: str
    about: str

@app.post("/api/save_profile")
def save_profile(profile: UserProfile):
    try:
        # Подключаемся к базе, которую ты создал в pgAdmin
        with psycopg.connect(DB_CONNECT) as conn:
            with conn.cursor() as cur:
                # 1. Записываем ник в таблицу users
                cur.execute("""
                    INSERT INTO users (tg_id, username, display_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (tg_id) DO UPDATE 
                    SET username = EXCLUDED.username, display_name = EXCLUDED.display_name;
                """, (profile.tg_id, profile.username, profile.display_name))
                
                # 2. Записываем ранг и описание в таблицу game_profiles
                cur.execute("""
                    INSERT INTO game_profiles (tg_id, game_name, rank, voice, about)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (tg_id, game_name) DO UPDATE 
                    SET rank = EXCLUDED.rank, voice = EXCLUDED.voice, about = EXCLUDED.about;
                """, (profile.tg_id, profile.game, profile.rank, profile.voice, profile.about))
                
                conn.commit()
        return {"status": "success", "message": "Данные сохранены в PostgreSQL!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))