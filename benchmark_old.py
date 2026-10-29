import time
import statistics
from app.database.db_ops import Database

# ===== ЗАПИСЬ (S2) =====
times_write = []
print("Замер 100 операций (Запись, старый код)...")
for i in range(100):
    start = time.perf_counter()
    Database.add_favorite_color(999, f"#FF57{i:02X}")
    end = time.perf_counter()
    times_write.append((end - start) * 1000)

print(f"ЛР0 Latency (Запись): p50={statistics.median(times_write):.2f}ms, p95={statistics.quantiles(times_write, n=20)[18]:.2f}ms")

# ===== ЧТЕНИЕ (S1) =====
times_read = []
print("Замер 100 операций (Чтение, старый код)...")
for _ in range(100):
    start = time.perf_counter()
    # Вызываем старый метод получения цветов
    Database.get_user_favorite_colors(999)
    end = time.perf_counter()
    times_read.append((end - start) * 1000)

print(f"ЛР0 Latency (Чтение): p50={statistics.median(times_read):.2f}ms, p95={statistics.quantiles(times_read, n=20)[18]:.2f}ms")