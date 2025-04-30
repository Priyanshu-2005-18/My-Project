import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os

# Set page configuration
st.set_page_config(page_title="BudgetBuddy", layout="wide")

# Custom CSS for improved styling, accessibility, and logo
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f7fa;
    }
    .header-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        flex-direction: column !important;
        margin: 0 auto !important;
        padding-top: 20px !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    .logo img {
        max-width: 600px !important;
        width: 100% !important;
        height: auto !important;
        margin: 0 auto !important;
        display: block !important;
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
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for expenses and transactions
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])

# Function to add an expense
def add_expense(date, category, amount, description):
    new_expense = pd.DataFrame({
        'Date': [date],
        'Category': [category],
        'Amount': [amount],
        'Description': [description]
    })
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
    st.rerun()

# Function to add a transaction
def add_transaction(date, person, transaction_type, amount, description):
    new_transaction = pd.DataFrame({
        'Date': [date],
        'Person': [person],
        'Type': [transaction_type],
        'Amount': [amount],
        'Description': [description]
    })
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
    st.rerun()

# Function to calculate balance for each person
def calculate_balances(transactions):
    if transactions.empty:
        return pd.DataFrame(columns=['Person', 'Balance'])
    
    person_balances = {}
    for _, row in transactions.iterrows():
        person = row['Person']
        amount = row['Amount']
        if row['Type'] == 'Gave':
            person_balances[person] = person_balances.get(person, 0) - amount
        else:  # Received
            person_balances[person] = person_balances.get(person, 0) + amount
    
    balance_df = pd.DataFrame(list(person_balances.items()), columns=['Person', 'Balance'])
    balance_df['Balance'] = balance_df['Balance'].round(2)
    return balance_df

# Function to filter transactions
def filter_transactions(transactions, search_term=None):
    if search_term:
        search_term = search_term.lower()
        return transactions[transactions.apply(lambda row: search_term in str(row).lower(), axis=1)]
    return transactions

# Streamlit UI
# Use a relative path for the logo (assumes pic.jpg is in the same directory as the script)
logo_path = os.path.join(os.path.dirname(__file__), "pic.jpg")

# Use columns to center the logo above the welcome message
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    if os.path.exists(logo_path):
        st.image(logo_path, width=600)
    else:
        st.image("https://via.placeholder.com/600", width=600)
        st.warning("Could not find 'pic.jpg' in the script's directory. Using a placeholder image. Place 'pic.jpg' in the same folder as this script.")
    st.markdown('</div>', unsafe_allow_html=True)

# Show welcome message
st.markdown("<div class='success-message'>Welcome! We're glad you're here to track your expenses and transactions with BudgetBuddy.</div>", unsafe_allow_html=True)

# Tabs for Expenses and Transactions
tab1, tab2 = st.tabs(["Expenses", "Transactions"])

# Expenses Tab
with tab1:
    with st.form(key='expense_form', clear_on_submit=True):
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        date = st.date_input("Date", value=datetime.date.today(), key="expense_date")
        category = st.selectbox("Category", ["Food", "Transport", "Utilities", "Entertainment", "Other"], key="expense_category")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="expense_amount")
        description = st.text_input("Description", placeholder="e.g., grocery shopping", key="expense_description")
        submit_button = st.form_submit_button("Add Expense")

        if submit_button:
            if not amount or amount <= 0:
                st.markdown("<div class='error-message'>Please enter a valid amount greater than 0.</div>", unsafe_allow_html=True)
            else:
                add_expense(date, category, amount, description)
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

        plt.figure(figsize=(6, 3))
        ax = sns.barplot(data=st.session_state.expenses, x='Category', y='Amount', estimator=sum, palette=color_palette)
        plt.title("Total Expenses by Category", fontsize=12, pad=10)
        plt.xticks(rotation=45, fontsize=8)
        plt.ylabel("Total Amount (₹)", fontsize=8)
        plt.xlabel("Category", fontsize=8)
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

    if st.button("Clear All Expenses"):
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        st.markdown("<div class='success-message'>All expenses cleared in BudgetBuddy!</div>", unsafe_allow_html=True)
        st.rerun()

# Transactions Tab
with tab2:
    with st.form(key='transaction_form', clear_on_submit=True):
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        date = st.date_input("Date", value=datetime.date.today(), key="transaction_date")
        person = st.text_input("Person's Name", placeholder="e.g., Priyanshu, Rohan", help="Enter the person's full name (e.g., Priyanshu, Rohan)")
        transaction_type = st.selectbox("Type", ["Gave", "Received"], key="transaction_type")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="transaction_amount")
        description = st.text_input("Description", placeholder="e.g., loan, gift", key="transaction_description")
        submit_button = st.form_submit_button("Add Transaction")

        if submit_button:
            if not amount or amount <= 0:
                st.markdown("<div class='error-message'>Please enter a valid amount greater than 0.</div>", unsafe_allow_html=True)
            elif not person.strip():
                st.markdown("<div class='error-message'>Please enter a person's name.</div>", unsafe_allow_html=True)
            else:
                add_transaction(date, person, transaction_type, amount, description)
                st.markdown("<div class='success-message'>Transaction added to BudgetBuddy!</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    search_term = st.text_input("Search Transactions (by name, date, or description)", placeholder="e.g., Priyanshu, 2025-02-21", key="transaction_search")

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
            balances_styled = balances.style.format({'Balance': '₹{:+.2f}'})
            st.dataframe(balances_styled.set_table_attributes('class="balance-table" style="width: 100%;"'))
        else:
            st.info("No balances to display in BudgetBuddy.")
        st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.transactions.empty:
        person_to_delete = st.text_input("Delete Transactions for Person", placeholder="e.g., Priyanshu, Rohan", key="delete_person")
        if st.button("Delete Transactions", key="delete_button"):
            if person_to_delete.strip():
                st.session_state.transactions = st.session_state.transactions[
                    st.session_state.transactions['Person'] != person_to_delete.strip()
                ]
                st.markdown("<div class='success-message'>Transactions for {} deleted in BudgetBuddy!</div>".format(person_to_delete), unsafe_allow_html=True)
                st.rerun()

    if st.button("Clear All Transactions"):
        if st.session_state.transactions.empty:
            st.markdown("<div class='error-message'>No transactions to clear in BudgetBuddy.</div>", unsafe_allow_html=True)
        else:
            if st.button("Confirm Clear All Transactions", key="confirm_clear"):
                st.session_state.transactions = pd.DataFrame(columns=['Date', 'Person', 'Type', 'Amount', 'Description'])
                st.markdown("<div class='success-message'>All transactions cleared in BudgetBuddy!</div>", unsafe_allow_html=True)
                st.rerun()

    if (not st.session_state.expenses.empty or not st.session_state.transactions.empty) and st.button("Export All Data as CSV"):
        combined_data = pd.concat([st.session_state.expenses.assign(Type='Expense'), 
                                  st.session_state.transactions.assign(Category='Transaction')], ignore_index=True)
        combined_data.to_csv("budgetbuddy_data.csv", index=False)
        st.markdown("<div class='success-message'>All data exported successfully as 'budgetbuddy_data.csv' in BudgetBuddy!</div>", unsafe_allow_html=True)