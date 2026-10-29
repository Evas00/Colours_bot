import asyncio
import time
import statistics
from app.container import Container

async def main():
    container = Container()
    
    # === ПРОГРЕВ ===
    print("Прогрев...")
    for _ in range(10):
        await container.add_color.execute(999, "#FFFFFF")
        await container.list_colors.execute(999)
    
    # === S2: ЗАПИСЬ ===
    times_write = []
    print("Замер 100 операций (Запись S2)...")
    for i in range(100):
        start = time.perf_counter()
        await container.add_color.execute(999, f"#FF57{i:02X}")
        end = time.perf_counter()
        times_write.append((end - start) * 1000)
        
    print(f"Latency (Запись): p50={statistics.median(times_write):.2f}ms, p95={statistics.quantiles(times_write, n=20)[18]:.2f}ms, p99={statistics.quantiles(times_write, n=100)[98]:.2f}ms")

    # === S1: ЧТЕНИЕ ===
    times_read = []
    print("Замер 100 операций (Чтение S1)...")
    for _ in range(100):
        start = time.perf_counter()
        await container.list_colors.execute(999)
        end = time.perf_counter()
        times_read.append((end - start) * 1000)
        
    print(f"Latency (Чтение): p50={statistics.median(times_read):.2f}ms, p95={statistics.quantiles(times_read, n=20)[18]:.2f}ms, p99={statistics.quantiles(times_read, n=100)[98]:.2f}ms")

if __name__ == "__main__":
    asyncio.run(main())