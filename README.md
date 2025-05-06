# Expense/ Transaction Tracker
A user-friendly web application designed to help individuals manage their finances by tracking expenses and peer-to-peer transactions. It offers visualizations, balance summaries, an accessible UI, and export features to provide a comprehensive financial overview.

Features
  1. Expense Tracking: Record and categorize your daily expenses effortlessly.
  2.Peer-to-Peer Transactions: Log and monitor transactions between individuals.
  3.Visualizations: Gain insights through charts and graphs representing your financial data.
  4.Balance Summaries: View summaries of your financial status at a glance.
  5.Export Functionality: Download your financial data for offline access or further analysis.

Technologies Used
  1.Frontend & Framework:
      Streamlit for interactive web app development
      HTML/CSS (embedded) for custom styling
  2.Data Management:
      Pandas for in-memory data handling (expenses and transactions)
  3.Data Visualization:
      Matplotlib and Seaborn for bar and line charts
  4.Image Processing:
      Pillow for displaying the app logo (pic.jpg)
  5.Proposed Database:
      SQLite for persistent data storage (see Database Integration)
  Tools:
      Python 3.8+ for backend logic
      Git for version control

Getting Started
  Prerequisites
  Python 3.x installed on your machine.

Installation
  1. Clone the repository:
      git clone https://github.com/Priyanshu-2005-18/My-Project.git
  2. Navigate to the project directory:
      cd BudgetBuddy
  3. Set up a virtual environment (recommended):
       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
  4. Install the required dependencies:
      pip install -r requirements.txt
  5.Add the logo:
      Place pic.jpg in the project root directory for the app’s header image.
  6. Run the application:
      streamlit run budgetbuddy.py



Project Structure
My-Project/
├── budgetbuddy.py         # Main Streamlit app
├── data/                  # Folder to store data files
├── requirements.txt       # List of required Python packages
└── README.md     
