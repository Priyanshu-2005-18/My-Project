import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import sqlite3
import os
import bcrypt
import re

st.set_page_config(page_title="BudgetBuddy", layout="wide")

st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f7fa;
        margin: 0;
        padding: 0;
    }
    .header-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        flex-direction: column !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 20px 0 !important;
        text-align: center !important;
        box-sizing: border-box !important;
    }
    .logo {
        display: block !important;
        margin: 0 auto !important;
        text-align: center !important;
    }
    .logo img {
        max-width: 600px !important;
        width: 100% !important;
        height: auto !important;
        margin: 0 auto !important;
        display: block !important;
        border-radius: 8px !important;
    }
    .form-container, .data-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stForm {
        padding: 0;
    }
    .dataframe {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .balance-table {
        font-size: 14px;
        border-collapse: collapse;
        width: 100%;
        margin-top: 15px;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .balance-table th, .balance-table td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid #e9ecef;
    }
    .balance-table th {
        background-color: #e9ecef;
        color: #2c3e50;
        font-weight: 600;
        border-radius: 12px 12px 0 0;
    }
    .stButton>button {
        background-color: #e74c3c;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #c0392b;
    }
    .stTextInput, .stSelectbox, .stNumberInput, .stDateInput {
        margin-bottom: 15px;
    }
    .stTextInput > div > input, .stSelectbox > div > select, .stNumberInput > div > input, .stDateInput > div > input {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }
    .stTextInput > div > input:focus, .stSelectbox > div > select:focus, .stNumberInput > div > input:focus, .stDateInput > div > input:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 5px rgba(52, 152, 219, 0.5);
    }
    .stSubheader {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 20px;
    }
    .error-message {
        color: #e74c3c;
        background-color: #ffebee;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 14px;
    }
    .success-message {
        color: #27ae60;
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 14px;
    }
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #2c3e50;
        color: #fff;
        text-align: center;
        padding: 5px;
        border-radius: 6px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
    .stColumns {
        justify-content: center !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    .stColumn {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .stContainer {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def init_db():
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (user_id INTEGER, date TEXT, category TEXT, amount REAL, description TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (user_id INTEGER, date TEXT, person TEXT, type TEXT, amount REAL, description TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute("PRAGMA table_info(expenses)")
    columns = [col[1] for col in c.fetchall()]
    if 'user_id' not in columns:
        c.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER")
        c.execute("UPDATE expenses SET user_id = 1 WHERE user_id IS NULL")
    c.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in c.fetchall()]
    if 'user_id' not in columns:
        c.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")
        c.execute("UPDATE transactions SET user_id = 1 WHERE user_id IS NULL")
    conn.commit()
    conn.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except Exception as e:
        st.error(f"Password verification error: {e}")
        return False

def register_user(email, password):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", 
                  (email.lower(), hash_password(password)))
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    except Exception as e:
        return False, f"Registration error: {e}"
    finally:
        conn.close()

def reset_password(email, new_password):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format."
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
    user = c.fetchone()
    if user:
        try:
            c.execute("UPDATE users SET password = ? WHERE email = ?", 
                      (hash_password(new_password), email.lower()))
            conn.commit()
            return True, "Password reset successful!"
        except Exception as e:
            return False, f"Password reset error: {e}"
        finally:
            conn.close()
    return False, "Email not found."

def login_user(email, password):
    conn = sqlite3.connect('budgetbuddy.db')
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE email = ?", (email.lower(),))
    user = c.fetchone()
    conn.close()
    if not user:
        return False, "Email not found."
    if verify_password(password, user[1]):
        return True, user[0]
    return False, "Incorrect password."

def load_data(user_id):
    try:
        conn = sqlite3.connect('budgetbuddy.db')
        expenses = pd.read_sql('SELECT * FROM expenses WHERE user_id = ?', conn, params=(user_id,))
        transactions = pd.read_sql('SELECT * FROM transactions WHERE user_id = ?', conn, params=(user_id,))
        conn.close()
        if not expenses.empty:
            if 'date' in expenses.columns:
                expenses['Date'] = pd.to_datetime(expenses['date'])
                expenses = expenses.drop(columns=['date', 'user_id'])
            else:
                expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        else:
            expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        if not transactions.empty:
            if 'date' in transactions.columns:
                transactions['Date'] = pd.to_datetime(transactions['date'])
                transactions = transactions.drop(columns=['date', 'user_id'])
            else:
                transactions = pd.DataFrame(columns=['Date', "Person", 'Type', 'Amount', 'Description'])
        else:
            transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])
        st.session_state.expenses = expenses
        st.session_state.transactions = transactions
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        st.session_state.transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])

def save_expenses(user_id):
    conn = sqlite3.connect('budgetbuddy.db')
    expenses = st.session_state.expenses.copy()
    if not expenses.empty:
        expenses['user_id'] = user_id
        expenses['date'] = expenses['Date'].astype(str)
        expenses = expenses[['user_id', 'date', 'Category', 'Amount', 'Description']]
        expenses.to_sql('expenses', conn, if_exists='replace', index=False, dtype={'date': 'TEXT'})
    else:
        conn.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def save_transactions(user_id):
    conn = sqlite3.connect('budgetbuddy.db')
    transactions = st.session_state.transactions.copy()
    if not transactions.empty:
        transactions['user_id'] = user_id
        transactions['date'] = transactions['Date'].astype(str)
        transactions = transactions[['user_id', 'date', 'Person', 'Type', 'Amount', 'Description']]
        transactions.to_sql('transactions', conn, if_exists='replace', index=False, dtype={'date': 'TEXT'})
    else:
        conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_expense(user_id, date, category, amount, description):
    new_expense = pd.DataFrame({
        'Date': [date],
        'Category': [category],
        'Amount': [amount],
        'Description': [description]
    })
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
    save_expenses(user_id)
    st.rerun()

def add_transaction(user_id, date, person, transaction_type, amount, description):
    new_transaction = pd.DataFrame({
        'Date': [date],
        'Person': [person],
        'Type': [transaction_type],
        'Amount': [amount],
        'Description': [description]
    })
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
    save_transactions(user_id)
    st.rerun()

def calculate_balances(transactions):
    if transactions.empty:
        return pd.DataFrame(columns=['Person', 'Balance'])
    person_balances = {}
    for _, row in transactions.iterrows():
        person = row['Person']
        amount = row['Amount']
        if row['Type'] == 'Gave':
            person_balances[person] = person_balances.get(person, 0) - amount
        else:
            person_balances[person] = person_balances.get(person, 0) + amount
    balance_df = pd.DataFrame(list(person_balances.items()), columns=['Person', 'Balance'])
    balance_df['Balance'] = balance_df['Balance'].round(2)
    return balance_df

def filter_transactions(transactions, search_term=None):
    if search_term:
        search_term = search_term.lower()
        return transactions[transactions.apply(lambda row: search_term in str(row).lower(), axis=1)]
    return transactions

init_db()

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])

if st.session_state.user_id is None:
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        logo_path = os.path.join(os.path.dirname(__file__), "pic.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=600, caption=None, use_column_width=False, output_format="auto")
        else:
            st.image("https://via.placeholder.com/600", width=600, caption=None, use_column_width=False, output_format="auto")
            st.warning("Logo 'pic.jpg' not found. Ensure it's in the app's directory.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div class='success-message'>Welcome to BudgetBuddy! Please log in or sign up to continue.</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])
    with tab1:
        with st.form(key='login_form', clear_on_submit=True):
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="e.g., user@example.com", key="login_email", help="Enter your email address")
            password = st.text_input("Password", type="password", key="login_password", help="Enter your password")
            submit_button = st.form_submit_button("Login", help="Log in to your account", args={'aria-label': 'Log in'})
            if submit_button:
                success, result = login_user(email, password)
                if success:
                    st.session_state.user_id = result
                    load_data(result)
                    st.markdown("<div class='success-message'>Logged in successfully!</div>", unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown(f"<div class='error-message'>{result}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    with tab2:
        with st.form(key='signup_form', clear_on_submit=True):
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="e.g., user@example.com", key="signup_email", help="Enter a valid email address")
            password = st.text_input("Password", type="password", key="signup_password", help="Choose a password (minimum 6 characters)")
            submit_button = st.form_submit_button("Sign Up", help="Create a new account", args={'aria-label': 'Sign up'})
            if submit_button:
                success, message = register_user(email, password)
                if success:
                    st.markdown("<div class='success-message'>{}</div>".format(message), unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='error-message'>{message}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    with tab3:
        with st.form(key='reset_form', clear_on_submit=True):
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="e.g., user@example.com", key="reset_email", help="Enter your email address")
            new_password = st.text_input("New Password", type="password", key="reset_password", help="Enter a new password (minimum 6 characters)")
            submit_button = st.form_submit_button("Reset Password", help="Reset your password", args={'aria-label': 'Reset password'})
            if submit_button:
                success, message = reset_password(email, new_password)
                if success:
                    st.markdown("<div class='success-message'>{}</div>".format(message), unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='error-message'>{message}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
else:
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        logo_path = os.path.join(os.path.dirname(__file__), "pic.jpg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=600, caption=None, use_column_width=False, output_format="auto")
        else:
            st.image("https://via.placeholder.com/600", width=600, caption=None, use_column_width=False, output_format="auto")
            st.warning("Logo 'pic.jpg' not found. Ensure it's in the app's directory.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div class='success-message'>Welcome back to BudgetBuddy! Track your expenses and transactions below.</div>", unsafe_allow_html=True)
    if st.button("Logout", help="Log out of your account", args={'aria-label': 'Log out'}):
        st.session_state.user_id = None
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        st.session_state.transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])
        st.markdown("<div class='success-message'>Logged out successfully!</div>", unsafe_allow_html=True)
        st.rerun()
    tab1, tab2 = st.tabs(["Expenses", "Transactions"])
    with tab1:
        with st.form(key='expense_form', clear_on_submit=True):
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            date = st.date_input("Date", value=datetime.date.today(), key="expense_date", help="Select the date of the expense")
            category = st.selectbox("Category", ["Food", "Transport", "Utilities", "Entertainment", "Other"], key="expense_category", help="Choose the expense category")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="expense_amount", help="Enter the expense amount")
            description = st.text_input("Description", placeholder="e.g., grocery shopping", key="expense_description", help="Provide a brief description")
            submit_button = st.form_submit_button("Add Expense", help="Submit the expense", args={'aria-label': 'Submit expense'})
            if submit_button:
                if not amount or amount <= 0:
                    st.markdown("<div class='error-message'>Please enter a valid amount greater than 0.</div>", unsafe_allow_html=True)
                else:
                    add_expense(st.session_state.user_id, date, category, amount, description)
                    st.markdown("<div class='success-message'>Expense added to BudgetBuddy!</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.subheader("Your Expenses")
        if not st.session_state.expenses.empty:
            st.dataframe(st.session_state.expenses.style.format({'Amount': '₹{:.2f}', 'Date': lambda x: x.strftime('%Y-%m-%d')})
                        .set_table_attributes('style="width: 100%; overflow-x: auto;"'))
        else:
            st.info("No expenses recorded in BudgetBuddy yet.")
        if not st.session_state.expenses.empty:
            st.subheader("Expense Visualization")
            color_palette = sns.color_palette("husl", len(st.session_state.expenses['Category'].unique()))
            category_sums = st.session_state.expenses.groupby('Category')['Amount'].sum()
            st.write("Debug - Total Expenses by Category:", category_sums)
            plt.figure(figsize=(6, 3))
            ax = sns.barplot(data=st.session_state.expenses, x='Category', y='Amount', estimator=sum, palette=color_palette, ci=None)
            plt.title("Total Expenses by Category", fontsize=12, pad=10)
            plt.xticks(rotation=45, fontsize=8)
            plt.ylabel("Total Amount (₹)", fontsize=8)
            plt.xlabel("Category", fontsize=8)
            plt.ylim(0, 5000)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_color('black')
            ax.spines['left'].set_color('black')
            ax.spines['bottom'].set_linewidth(1.5)
            ax.spines['left'].set_linewidth(0.5)
            ax.grid(False)
            plt.margins(x=0.2, y=0.1)
            st.pyplot(plt)
            plt.close()
            plt.figure(figsize=(6, 3))
            expenses_over_time = st.session_state.expenses.groupby('Date')['Amount'].sum().reset_index()
            ax = sns.lineplot(data=expenses_over_time, x='Date', y='Amount', marker='o', color='blue')
            plt.title("Expenses Over Time", fontsize=12, pad=10)
            plt.ylabel("Total Amount (₹)", fontsize=8)
            plt.xlabel("Date", fontsize=8)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_color('black')
            ax.spines['left'].set_color('black')
            ax.spines['bottom'].set_linewidth(1.5)
            ax.spines['left'].set_linewidth(0.5)
            ax.grid(False)
            plt.margins(x=0.2, y=0.1)
            st.pyplot(plt)
            plt.close()
            plt.figure(figsize=(6, 3))
            category_sums = st.session_state.expenses.groupby('Category')['Amount'].sum()
            plt.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', colors=color_palette)
            plt.title("Expense Distribution by Category", fontsize=12)
            st.pyplot(plt)
            plt.close()
        if st.button("Clear All Expenses", help="Remove all expenses", args={'aria-label': 'Clear all expenses'}):
            st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
            save_expenses(st.session_state.user_id)
            st.markdown("<div class='success-message'>All expenses cleared in BudgetBuddy!</div>", unsafe_allow_html=True)
            st.rerun()
    with tab2:
        with st.form(key='transaction_form', clear_on_submit=True):
            st.markdown("<div class='form-container'>", unsafe_allow_html=True)
            date = st.date_input("Date", value=datetime.date.today(), key="transaction_date", help="Select the transaction date")
            person = st.text_input("Person's Name", placeholder="e.g., Eesha, Priyanshu", help="Enter the person's full name")
            transaction_type = st.selectbox("Type", ["Gave", "Received"], key="transaction_type", help="Choose whether you gave or received money")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="transaction_amount", help="Enter the transaction amount")
            description = st.text_input("Description", placeholder="e.g., loan, gift", key="transaction_description", help="Provide a brief description")
            submit_button = st.form_submit_button("Add Transaction", help="Submit the transaction", args={'aria-label': 'Submit transaction'})
            if submit_button:
                if not amount or amount <= 0:
                    st.markdown("<div class='error-message'>Please enter a valid amount greater than 0.</div>", unsafe_allow_html=True)
                elif not person.strip():
                    st.markdown("<div class='error-message'>Please enter a person's name.</div>", unsafe_allow_html=True)
                else:
                    add_transaction(st.session_state.user_id, date, person, transaction_type, amount, description)
                    st.markdown("<div class='success-message'>Transaction added to BudgetBuddy!</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        search_term = st.text_input("Search Transactions (by name, date, or description)", placeholder="e.g., Eesha, 2025-02-21", key="transaction_search", help="Search transactions by any keyword")
        st.subheader("Your Transactions")
        if not st.session_state.transactions.empty:
            filtered_transactions = filter_transactions(st.session_state.transactions, search_term)
            sorted_transactions = filtered_transactions.sort_values(by='Date', ascending=False)
            st.markdown("<div class='data-container' role='table' aria-label='Transaction List'>", unsafe_allow_html=True)
            st.dataframe(sorted_transactions.style.format({'Amount': '₹{:.2f}', 'Date': lambda x: x.strftime('%Y-%m-%d')})
                        .set_table_attributes('style="width: 100%; overflow-x: auto;"'))
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No transactions recorded in BudgetBuddy yet.")
        if not st.session_state.transactions.empty:
            st.subheader("Balances with People")
            st.markdown("<div class='data-container' role='table' aria-label='Balance Summary'>", unsafe_allow_html=True)
            balances = calculate_balances(st.session_state.transactions)
            if not balances.empty:
                balances_styled = balances.style.format({'Balance': lambda x: f"₹{x:+.2f}"})
                st.dataframe(balances_styled.set_table_attributes('class="balance-table" style="width: 100%;"'))
            else:
                st.info("No balances to display in BudgetBuddy.")
            st.markdown("</div>", unsafe_allow_html=True)
        if not st.session_state.transactions.empty:
            person_to_delete = st.text_input("Delete Transactions for Person", placeholder="e.g., Eesha, Priyanshu", key="delete_person", help="Enter the person's name to delete their transactions")
            if st.button("Delete Transactions", key="delete_button", help="Delete transactions for the specified person", args={'aria-label': 'Delete transactions'}):
                if person_to_delete.strip():
                    st.session_state.transactions = st.session_state.transactions[
                        st.session_state.transactions['Person'] != person_to_delete.strip()
                    ]
                    save_transactions(st.session_state.user_id)
                    st.markdown("<div class='success-message'>Transactions for {} deleted in BudgetBuddy!</div>".format(person_to_delete), unsafe_allow_html=True)
                    st.rerun()
        if st.button("Clear All Transactions", help="Remove all transactions", args={'aria-label': 'Clear all transactions'}):
            if st.session_state.transactions.empty:
                st.markdown("<div class='error-message'>No transactions to clear in BudgetBuddy.</div>", unsafe_allow_html=True)
            else:
                st.warning("Are you sure you want to clear all transactions?")
                if st.button("Confirm", key="confirm_clear", help="Confirm clearing all transactions", args={'aria-label': 'Confirm clear transactions'}):
                    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])
                    save_transactions(st.session_state.user_id)
                    st.markdown("<div class='success-message'>All transactions cleared in BudgetBuddy!</div>", unsafe_allow_html=True)
                    st.rerun()
    if not st.session_state.expenses.empty or not st.session_state.transactions.empty:
        if st.button("Export All Data as CSV", help="Download all data as CSV", args={'aria-label': 'Export data as CSV'}):
            combined_data = pd.concat([st.session_state.expenses.assign(Type='Expense'), 
                                      st.session_state.transactions.assign(Category='Transaction')], ignore_index=True)
            csv = combined_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="budgetbuddy_data.csv",
                mime="text/csv",
                help="Click to download the CSV file",
                args={'aria-label': 'Download CSV file'}
            )
            st.markdown("<div class='success-message'>CSV ready for download!</div>", unsafe_allow_html=True)
