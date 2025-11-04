from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.database import get_connection
import subprocess, tempfile, os

app = FastAPI()

# Фронтенд на /frontend
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

tasks = [
    {
        "id": 1,
        "title": "Сумма двух чисел | Iki ədədin cəmi",
        "description": """русский:
Вводятся два числа, выведите их сумму.
0 < a, b < 100000
Примеры:
ввод
1 2
вывод
3

azerbaycan dili:
İki ədəd verilir, onların cəmini çıxarın.
0 < a, b < 100000
Nümunələr:
Giriş
1 2
Çıxış
3""",
        "tests": [
            {"input": "2 3\n", "output": "5"},
            {"input": "10 20\n", "output": "30"},
            {"input": "10000 12121\n", "output": "22121"},
            {"input": "1 23232\n", "output": "23233"}
        ]
    },
    {
        "id": 2,
        "title": "Умножение чисел | İki ədədin vurulması",
        "description": """русский:
Вводятся два числа, выведите их произведение.
0 <= a,b <= 1000000
Примеры:
ввод
10 10
вывод
100

azerbaycan dili:
İki ədəd verilir, onların hasilini çıxarın.
0 <= a, b <= 1000000
Nümunələr:
Giriş
10 10
Çıxış
100""",
        "tests": [
            {"input": "2 3\n", "output": "6"},
            {"input": "10 20\n", "output": "200"},
            {"input": "1000000 1000000\n", "output": "1000000000000"},
            {"input": "0 1000000\n", "output": "0"},
        ]
    },
    {
        "id": 3,
        "title": "Королевские кони | Kral atları",
        "description": """
русский:
Даётся поле n*n. Вы должны вывести количество способов расставить m шахматных коней так, 
чтобы ни один конь не бил другого и кони не были поставлены рядом по горизонтали или по вертикали.
1 <= n <= 10 | 1 <= m <=n
Примеры:
ввод
3 2
вывод
16

azerbaycan dili:
n*n ölçülü sahə verilir. Siz m şahmat atını yerləşdirməyin yollarının sayını çıxarmalısınız
belə ki, heç bir at digərini vura bilməsin və atlar yan-yana
şaquli və üfüqi xətt üzrə yerləşdirilməsin.
1 <= n <= 10 | 1 <= m <= n
Nümunə:
Giriş
3 2
Çıxış
16""",
        "tests": [
            {"input": "1 1\n", "output": "1"},
            {"input": "2 1\n", "output": "4"},
            {"input": "4 2\n", "output": "72"},
            {"input": "5 5\n", "output": "2999"},
            {"input": "7 3\n", "output": "10478"},
            {"input": "8 4\n", "output": "262549"},
            {"input": "9 5\n", "output": "7807853"},
        ]
    }
]

@app.post("/submit/")
async def submit_code(
    username: str = Form(...),
    problem_id: int = Form(...),
    code: UploadFile = Form(...)
):
    task = next((t for t in tasks if t["id"] == problem_id), None)
    if not task:
        return {"status": "error", "message": "Задача не найдена"}

    # Создаём временный файл для кода
    content = await code.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as tmp:
        code_path = tmp.name
        tmp.write(content)
    exe_path = code_path.replace(".cpp", "")

    # Компиляция
    compile_proc = subprocess.run(
        ["g++", code_path, "-o", exe_path],
        capture_output=True, text=True
    )
    if compile_proc.returncode != 0:
        os.remove(code_path)
        return JSONResponse({"status":"compile_error", "message": compile_proc.stderr})

    # Запуск тестов
    passed = 0
    total = len(task["tests"])
    for t in task["tests"]:
        try:
            run_proc = subprocess.run(
                exe_path,
                input=t["input"],
                text=True,
                capture_output=True,
                timeout=3
            )
            output = run_proc.stdout.strip()
            if output == t["output"].strip():
                passed += 1
        except subprocess.TimeoutExpired:
            continue

    score = int((passed / total) * 100)

    # Сохраняем результат в БД
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users(username) VALUES (?)", (username,))
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cur.fetchone()["id"]

    # Проверяем, решал ли уже задачу на 100%
    cur.execute(
        "SELECT COUNT(*) as cnt FROM submissions WHERE user_id = ? AND problem_id = ? AND score = 100",
        (user_id, problem_id)
    )
    already_solved = cur.fetchone()["cnt"] > 0

    # Вставляем новое решение
    cur.execute(
        "INSERT INTO submissions(user_id, problem_id, code, score) VALUES (?,?,?,?)",
        (user_id, problem_id, content.decode(), score)
    )

    # Увеличиваем solved_count только если ещё не решал задачу на 100%
    if score == 100 and not already_solved:
        cur.execute("UPDATE users SET solved_count = solved_count + 1 WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    # Удаляем временные файлы
    os.remove(code_path)
    if os.path.exists(exe_path):
        os.remove(exe_path)

    return {
        "status": "success",
        "score": score,
        "passed": passed,
        "total": total
    }

@app.get("/leaderboard/")
def leaderboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, solved_count FROM users ORDER BY solved_count DESC LIMIT 10")
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return data

@app.get("/tasks/")
def get_tasks():
    return [{"id": t["id"], "title": t["title"], "description": t["description"]} for t in tasks]
#sqlite3 database.db
#python -m uvicorn backend.main:app --reload