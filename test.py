from flask import Flask,flash, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# 路由：首頁
@app.route('/')
def index():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    else:
        return redirect('/homepage')

@app.route('/homepage')
def homepage():
    return render_template('index.html')

# 建立資料庫連線
def create_connection():
    conn = sqlite3.connect('database.db')
    return conn

# 在資料庫中建立使用者資料表
def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# 在資料庫中建立記帳資料表
def create_expenses_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   category TEXT NOT NULL,
                   amount REAL NOT NULL,
                   note TEXT,
                   date TEXT NOT NULL,
                   budget REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

# 執行資料表建立
create_users_table()
create_expenses_table()

# 路由：使用者註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 從表單獲取使用者註冊資訊
        username = request.form['username']
        password = request.form['password']

        # 檢查帳號是否已存在於資料庫
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return render_template('register.html', message='帳號已存在')

            # 將使用者資訊儲存到資料庫
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()

            # 註冊成功，轉到註冊成功頁面，並傳遞訊息變數
            return render_template('registration_success.html', message='註冊成功')

    return render_template('register.html')

# 路由：使用者登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 從表單獲取使用者登入資訊
        username = request.form['username']
        password = request.form['password']

        # 在資料庫中驗證使用者資訊，這裡使用SQLite作為範例
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()

            if user:
                session['username'] = username
                return redirect('/')
            else:
                return render_template('login.html', message='帳號或密碼錯誤')

    return render_template('login.html')

# 路由：記帳頁面
@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # 從表單獲取記帳資訊
        category = request.form['category']
        note = request.form['note']
        amount = float(request.form['amount'])
<<<<<<< HEAD
        record_type = request.form['record_type']
        date_today = date.today().strftime("%Y/%m/%d")
        budget = request.form.get('budget')
=======
        record_type = request.form['record_type']  # 新增的記錄類型欄位
        date_today = request.form['date']   # 取得選擇日期
>>>>>>> b15ed76b185eaef69971d03f660823b68b311c48
        # 根據記錄類型設置金額正負號
        if record_type == 'income':
            amount = abs(amount)
        else:
            amount = -abs(amount)

        # 將記帳資訊儲存到資料庫，這裡使用SQLite作為範例
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO expenses (username, category, note, amount, date, budget) VALUES (?, ?, ?, ?, ?, ?)',
                           (session['username'], category, note, amount,date_today, budget))
            conn.commit()

            # 打印调试信息
        print('Category:', category)
        print('Note:', note)
        print('Amount:', amount)
        print('Date:', date_today)

    # 從資料庫中獲取使用者的所有記帳資料
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE username = ? ORDER BY date', (session['username'],))
        expenses = cursor.fetchall()

        # 打印调试信息
        print('Expenses:', expenses)

        # 計算月總額和損益
        total_amount = sum(expense[3] for expense in expenses)
        profit_loss = calculate_profit_loss(expenses)
        # 排序支出記錄
        category = request.args.get('category')  # 從URL參數獲取用戶選擇的分類
        if category:
            expenses = sorted(expenses, key=lambda x: x[2] if x[2] == category else '')

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT budget FROM expenses WHERE username = ? AND budget IS NOT NULL', (session['username'],))
        budget_result = cursor.fetchone()
        budget = budget_result[0] if budget_result else None

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(expenses)')  # 獲取資料表結構
        columns = [column[1] for column in cursor.fetchall()]

        if 'category' not in columns:
            cursor.execute('ALTER TABLE expenses ADD COLUMN category TEXT')  # 添加 category 欄位

    return render_template('expense.html', expenses=expenses, total_amount=total_amount, profit_loss=profit_loss, budget=budget)

# 路由: 編輯記帳項目
@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if request.method == 'POST':
        category = request.form['category']
        note = request.form['note']
        amount = float(request.form['amount'])
        date_today = request.form['date']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE expenses SET category = ?, note = ?, amount = ?, date = ? WHERE id = ?',
                           (category, note, amount, date_today, expense_id))
            conn.commit()
            return redirect('/expense')
    else:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
            expense = cursor.fetchone()
        return render_template('edit.html', expense=expense)


# 路由：統計報表
@app.route('/report')
def report():
    if 'username' not in session:
        return redirect('/login')

    # 從資料庫中獲取使用者的所有記帳資料
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE username = ? ORDER BY date(date)', (session['username'],))
        expenses = cursor.fetchall()

    # 打印调试信息
    print('Expenses:', expenses)

    # 計算月總額和損益
    total_amount = sum(expense[3] for expense in expenses)
    income = sum(expense[3] for expense in expenses if expense[3] >= 0)
    expense = sum(expense[3] for expense in expenses if expense[3] < 0)

    # 打印调试信息
    print('Total Amount:', total_amount)
    print('Income:', income)
    print('Expense:', expense)
    return render_template('report.html', expenses=expenses, total_amount=total_amount, income=income, expense=expense)

# 計算損益
def calculate_profit_loss(expenses_data):
    income = sum(expense[3] for expense in expenses_data if expense[3] >= 0)
    expenses = sum(expense[3] for expense in expenses_data if expense[3] < 0)
    return income - abs(expenses)

# 路由：進階功能
@app.route('/advanced', methods=['GET', 'POST'])
def advanced():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        if 'set_budget' in request.form:
            set_budget(request.form)

    # 獲取支出類別佔比及預算數值
    categorized_expenses, category_budgets = get_expenses_and_budgets()
    all_categories = [expense[0] for expense in categorized_expenses]

    return render_template('advanced.html', categorized_expenses=categorized_expenses, category_budgets=category_budgets, all_categories=all_categories)

# 設定預算的函式
def set_budget(form_data):
    # 從表單中獲取每個類別的預算數值
    category_budgets = {}
    for key, value in form_data.items():
        if key.startswith('budget_'):
            category = key.split('_')[1]
            budget = float(value)
            category_budgets[category] = budget

    # 將預算存儲到資料庫中，關聯到當前使用者
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        for category, budget in category_budgets.items():
            cursor.execute('UPDATE expenses SET budget = ? WHERE username = ? AND category = ?', (budget, session['username'], category))
        conn.commit()

    flash('預算已設定成功！')

# 獲取支出類別佔比及預算數值的函式
def get_expenses_and_budgets():
    # 從資料庫中獲取使用者的所有支出資料
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT category, ABS(SUM(amount)) '
                       'FROM expenses '
                       'WHERE username = ? AND amount < 0 '
                       'GROUP BY category '
                       'HAVING SUM(amount) < 0',
                       (session['username'],))
        categorized_expenses = cursor.fetchall()

        # 總支出金額
        total_expenses = sum(expense[1] for expense in categorized_expenses)

    # 從資料庫中獲取使用者的支出類別及預算數值
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        # 獲取所有類別
        all_categories = ['食', '衣', '住', '行', '育', '樂']

        # 準備 SQL 查詢的參數
        query_params = [session['username']] + all_categories

        # 產生 SQL 查詢的佔位符
        placeholders = ','.join(['?'] * len(all_categories))

        # 查詢使用者的支出類別及預算數值
        query = f"SELECT category, budget FROM expenses WHERE username = ? AND category IN ({placeholders})"
        cursor.execute(query, query_params)
        category_budgets = dict(cursor.fetchall())

    # 處理未出現在支出紀錄中的類別
    missing_categories = set(all_categories) - set([expense[0] for expense in categorized_expenses])
    for category in missing_categories:
        category_budgets[category] = 0

    # 計算支出類別佔比
    categorized_expenses = [(expense[0], expense[1], round(expense[1] / total_expenses * 100, 2)) for expense in categorized_expenses]

    return categorized_expenses, category_budgets



# 路由：使用者登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/homepage')

if __name__ == '__main__':
    app.run(debug=True)
