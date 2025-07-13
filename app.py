import streamlit as st
import pandas as pd
from datetime import date
from categorizer import categorize_expense
from sklearn.linear_model import LinearRegression
import plotly.express as px
import openai

# Page setup
st.set_page_config(
    page_title="SmartNaira: AI Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

#  Apply Theme from .streamlit/config.toml
client = OpenAI(api_key=st.secrets.get("sk-proj-aAvTD2KcFoLXfRn4pi-0x9_3js-"
                                "XvI7_XVN5GKSbLBOyJOS2CzbGkg9cROqUOuUi22g4jMbCVsT3BlbkFJSx5oNuMtxzgVkydZCoPJwm26rOsORwbiB1h-"
                                "ZJQewKuQKyPNFQvmpcwUONMMbv81x0eZI50jsA"))

st.title("💰 SmartNaira: AI-Powered Expense Tracker")

DATA_FILE = "data.csv"
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Amount", "Type", "Description", "Payment Mode", "Category"])

#  Add Entry
with st.sidebar:
    st.header("Add a New Entry")
    with st.form("expense_form"):
        entry_date = st.date_input("Date", value=date.today())
        entry_type = st.selectbox("Type", ["Expense", "Income"])
        amount = st.number_input("Amount (₦)", min_value=0.0, format="%.2f")
        payment_mode = st.selectbox("Payment Mode", ["Cash", "POS", "Bank Transfer", "Others"])
        description = st.text_input("Description (e.g., Bought fuel, Salary)")
        submitted = st.form_submit_button("Save Entry")
        if submitted and amount > 0 and description:
            category = categorize_expense(description, entry_type)
            new_entry = pd.DataFrame([{
                "Date": entry_date,
                "Amount": amount,
                "Type": entry_type,
                "Description": description,
                "Payment Mode": payment_mode,
                "Category": category
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Entry saved under '{category}'")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "📊 Charts", "🤖 Chat Assistant"])

# ===== Dashboard Tab =====
with tab1:
    st.subheader("📋 Recent Transactions")
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        st.dataframe(df.tail(10), use_container_width=True)

        total_income = df[df['Type'] == 'Income']['Amount'].sum()
        total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
        balance = total_income - total_expense

        st.markdown("### 📈 Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"₦{total_income:,.2f}")
        col2.metric("Total Expense", f"₦{total_expense:,.2f}")
        col3.metric("Balance", f"₦{balance:,.2f}")
    else:
        st.info("No entries yet. Add your first above to begin.")

# ===== Charts Tab =====
with tab2:
    if not df.empty and not df[df["Type"] == "Expense"].empty:
        expense_data = df[df["Type"] == "Expense"]
        st.markdown("### 📌 Expenses by Category")
        pie_chart = px.pie(expense_data, names="Category", values="Amount", title="Expenses by Category")
        st.plotly_chart(pie_chart, use_container_width=True)

        st.markdown("### 📅 Daily Expense Trend")
        trend = expense_data.groupby("Date")["Amount"].sum().reset_index()
        trend_chart = px.line(trend, x="Date", y="Amount", title="Daily Expense Trend")
        st.plotly_chart(trend_chart, use_container_width=True)

        st.markdown("### 📈 Cumulative Spending Over Time")
        expense_data_sorted = expense_data.sort_values("Date")
        expense_data_sorted["Cumulative"] = expense_data_sorted["Amount"].cumsum()
        cumulative_chart = px.line(expense_data_sorted, x="Date", y="Cumulative", title="Cumulative Spending")
        st.plotly_chart(cumulative_chart, use_container_width=True)

        if len(trend) > 3:
            trend["Date"] = pd.to_datetime(trend["Date"])
            trend["Day"] = (trend["Date"] - trend["Date"].min()).dt.days
            X = trend[["Day"]]
            y = trend["Amount"]
            model = LinearRegression()
            model.fit(X, y)
            future_day = X["Day"].max() + 30
            prediction = model.predict([[future_day]])
            st.info(f"🔮 Estimated Spending in 30 Days: ₦{prediction[0]:,.2f}")
    else:
        st.warning("Not enough expense data to show charts yet.")

# ===== Chat Assistant Tab =====
with tab3:
    st.markdown("### 🤖 Ask SmartNaira")
    chat_query = st.text_input("Ask something like: 'How much did I spend on food?'")

    if chat_query and not df.empty:
        with st.spinner("Analyzing..."):
            try:
                prompt = f"""You are SmartNaira, a helpful Nigerian personal finance assistant.
Here are the user's financial records:

{df.to_string(index=False)}

Now answer this question based on the records: {chat_query}"""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You're a helpful assistant."},
                        {"role": "user", "content": "What's my budget?"}
                    ]
                )

                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"❌ OpenAI Error: {e}")
    elif chat_query:
        st.warning("No data available yet. Please add entries first.")

# Export & Reset Options
st.sidebar.markdown("---")
st.sidebar.header("🧾 Data Options")
st.sidebar.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name="smartnaira_data.csv", mime="text/csv")
if st.sidebar.button("🗑️ Reset All Entries"):
    df = pd.DataFrame(columns=["Date", "Amount", "Type", "Description", "Payment Mode", "Category"])
    df.to_csv(DATA_FILE, index=False)
    st.success("All data has been cleared.")
