import random
import time
from datetime import datetime, timedelta
from app.infrastructure.persistence.models import Session, User, ActionLog, Palette, PaletteColor

def generate_big_data(target_mb=2048):
    session = Session()
    print(f"🚀 Начинаем генерацию данных (цель: {target_mb} МБ)...")
    start_time = time.time()
    
    # Очищаем старую базу, чтобы не было дублей
    session.query(ActionLog).delete()
    session.query(PaletteColor).delete()
    session.query(Palette).delete()
    session.query(User).delete()
    session.commit()
    
    total_bytes = 0
    user_count = 0
    
    while total_bytes < target_mb * 1024 * 1024:
        user = User(telegram_id=random.randint(10000000, 99999999), username=f"user_{user_count}")
        session.add(user)
        session.flush()
        
        # Генерируем 1000 логов на пользователя
        logs = []
        for _ in range(1000):
            details = f'{{"data": "{"X" * 500}"}}' # Большой текст, чтобы быстрее набрать вес
            logs.append(ActionLog(
                user_id=user.id,
                action_type="simulate",
                details=details,
                timestamp=datetime.now()
            ))
        
        session.bulk_save_objects(logs)
        session.commit()
        
        user_count += 1
        if user_count % 50 == 0:
            import os
            current_size = os.path.getsize('data/colors.db')
            total_bytes = current_size
            print(f"✅ Сгенерировано {user_count} пользователей. Размер БД: {round(current_size / (1024 * 1024), 2)} МБ")
            
    session.close()
    print(f"🎉 Готово! Итоговый размер: {round(total_bytes / (1024 * 1024), 2)} МБ. Затрачено времени: {int(time.time() - start_time)} сек.")

if __name__ == "__main__":
    generate_big_data(2048) # Генерируем 2 ГБ