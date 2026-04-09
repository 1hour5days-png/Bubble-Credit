import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io
import zipfile

st.set_page_config(page_title="UltraFast Budget Tracker", layout="centered")

# Load or create CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("budget_data.csv")
        df["Date"] = df["Date"].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount"])

budget_df = load_data()

# Track last entry (for Quick Repeat)
if "last_entry" not in st.session_state:
    st.session_state.last_entry = None

st.title("⚡ UltraFast Budget Tracker")
st.write("Designed to be fast, simple, mobile-friendly, and easy to use.")

# ------------------------------
# FAST ENTRY UI
# ------------------------------

st.subheader("➕ Add a Transaction (Ultra-Fast Mode)")

# Better date input (calendar picker)
date = st.date_input("Select Date", datetime.date.today())

# Income / Expense quick buttons
col1, col2 = st.columns(2)
with col1:
    income_click = st.button("💰 Income")
with col2:
    expense_click = st.button("📉 Expense")

# Quick category buttons
st.write("Category:")
categories = ["Food", "Rent", "Bills", "Gas", "Shopping", "Travel", "Entertainment", "Medical", "Other"]

selected_category = st.radio("", categories, horizontal=True)

# Amount
amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")

# Voice Input (Browser microphone)
st.subheader("🎤 Voice Input")
st.write("Say something like: *Gas 40 dollars today*")

voice = st.text_input("Voice-to-Text (paste dictation here if needed)")

def parse_voice(text):
    text = text.lower()
    found_cat = None
    found_amt = None

    # Category extraction
    for cat in categories:
        if cat.lower() in text:
            found_cat = cat

    # Amount extraction
    words = text.split()
    for w in words:
        try:
            found_amt = float(w)
        except:
            pass

    return found_cat, found_amt


# Quick Add Logic
ttype = None
if income_click:
    ttype = "Income"
elif expense_click:
    ttype = "Expense"

# Voice parsing override
if voice.strip() != "":
    vcat, vamt = parse_voice(voice)
    if vcat is not None:
        selected_category = vcat
    if vamt is not None:
        amount = vamt
    st.info(f"Voice parsed → Category: {selected_category}, Amount: {amount}")

# Save transaction
if ttype and amount > 0:
    new_row = {
        "Date": date.strftime("%Y-%m-%d"),
        "Type": ttype,
        "Category": selected_category,
        "Amount": amount
    }
    budget_df = pd.concat([budget_df, pd.DataFrame([new_row])], ignore_index=True)
    budget_df.to_csv("budget_data.csv", index=False)
    st.session_state.last_entry = new_row
    st.success(f"{ttype} of ${amount:.2f} added!")

# Repeat last entry
if st.session_state.last_entry:
    if st.button("🔁 Repeat Last Transaction"):
        budget_df = pd.concat([budget_df, pd.DataFrame([st.session_state.last_entry])], ignore_index=True)
        budget_df.to_csv("budget_data.csv", index=False)
        st.success("Repeated last transaction!")


# ------------------------------
# MONTH FILTER
# ------------------------------
st.subheader("📅 Filter by Month")

month = st.selectbox(
    "Choose Month",
    ["All"] + [f"{i:02d}" for i in range(1, 13)]
)

if month != "All":
    filtered_df = budget_df[budget_df["Date"].str[5:7] == month]
else:
    filtered_df = budget_df

st.dataframe(filtered_df)

# ------------------------------
# SUMMARY
# ------------------------------
income = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
remaining = income - expense

st.subheader("💰 Summary")
st.write(f"**Total Income:** ${income:.2f}")
st.write(f"**Total Expense:** ${expense:.2f}")
st.write(f"**Remaining Budget:** ${remaining:.2f}")

# ------------------------------
# PIE CHART
# ------------------------------
expense_df = filtered_df[filtered_df["Type"] == "Expense"]

if not expense_df.empty:
    st.subheader("🍕 Expense Breakdown")
    fig, ax = plt.subplots()
    pie_data = expense_df.groupby("Category")["Amount"].sum()
    ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%")
    st.pyplot(fig)
else:
    st.info("No expenses to show.")


# ------------------------------
# DOWNLOAD THE ENTIRE APP (ZIP)
# ------------------------------
st.subheader("📥 Download the Entire App")

def create_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.write("app.py")
        z.write("requirements.txt")

        try:
            z.write("budget_data.csv")
        except:
            pass

    buffer.seek(0)
    return buffer

zip_file = create_zip()

st.download_button(
    label="Download Budget Tracker ZIP",
    data=zip_file,
    file_name="budget_tracker_app.zip",
    mime="application/zip"
)

st.write("This ZIP includes the full app and data. Run it with:")
st.code("streamlit run app.py")
