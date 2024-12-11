# app.py
import duckdb
import pandas as pd
import streamlit as st

# MotherDuck token and database connection
motherduck_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sczEyMDIzQGJ5dWkuZWR1Iiwic2Vzc2lvbiI6Im9sczEyMDIzLmJ5dWkuZWR1IiwicGF0IjoiTmpYbGd3ZXlXMUJjaXY2dEpMQUl6b1ozenV2RVhPNHVoYi00YTc4VUtKTSIsInVzZXJJZCI6IjY3ZDYzMWRmLTgzMjktNDhjYi04ZjRhLTk4MWI4YTI3ODVhMiIsImlzcyI6Im1kX3BhdCIsInJlYWRPbmx5IjpmYWxzZSwidG9rZW5UeXBlIjoicmVhZF93cml0ZSIsImlhdCI6MTczMzYwNzk4NX0.cesuoNv2A4wTfW7j7z2grEutIkVnLyRgrv7VYzP_RBE'  # Replace with your valid token
con = duckdb.connect(f"md:TestDB?motherduck_token={motherduck_token}")

# Ensure the required tables exist
try:
    con.sql("""
        CREATE TABLE IF NOT EXISTS users (
            paddle_number TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT
        )
    """)
    con.sql("""
        CREATE TABLE IF NOT EXISTS sales (
            paddle_number TEXT,
            item_number TEXT,
            amount INT,
            FOREIGN KEY (paddle_number) REFERENCES users(paddle_number)
        )
    """)
except Exception as e:
    st.error(f"Error creating tables: {e}")

# Navigation logic using session state
if "page" not in st.session_state:
    st.session_state["page"] = "register"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def set_page(page):
    st.session_state["page"] = page

def authenticate(password):
    if password == "1234567":
        st.session_state["authenticated"] = True
        st.success("Password correct")
        set_page("admin")
    else:
        st.error("Try again")

# Registration Page
if st.session_state["page"] == "register":
    st.title("Auction Participant Registration")
    paddle_number = st.text_input("Paddle Number")
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")

    if st.button("Register"):
        if paddle_number and name and phone:
            query = f"""
                INSERT INTO users (paddle_number, name, phone)
                VALUES ('{paddle_number}', '{name}', '{phone}')
            """
            try:
                con.sql(query)
                st.success(f"Participant {name} with Paddle Number {paddle_number} has been registered successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please fill in all fields.")

    # Button to go to the password-protected admin page
    if st.button("Go to Admin Page"):
        set_page("password")

# Password Page
elif st.session_state["page"] == "password":
    st.title("Admin Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Submit"):
        authenticate(password)

# Admin Page
elif st.session_state["page"] == "admin" and st.session_state["authenticated"]:
    st.title("Admin Dashboard")

    # Search Sales by Paddle Number
    st.header("Search Sales by Paddle Number")
    search_paddle = st.text_input("Enter Paddle Number to Search")
    if st.button("Search Paddle"):
        try:
            search_query = f"""
                SELECT 
                    u.paddle_number, u.name, u.phone, s.item_number, s.amount 
                FROM users AS u 
                LEFT JOIN sales AS s 
                ON u.paddle_number = s.paddle_number
                WHERE u.paddle_number = '{search_paddle}'
            """
            search_result = con.sql(search_query).df()
            
            if not search_result.empty:
                st.write(f"Sales for Paddle Number: {search_paddle}")
                st.dataframe(search_result)
                total_amount = search_result['amount'].fillna(0).sum()
                st.write(f"**Total Amount for Paddle {search_paddle}: ${total_amount}**")
            else:
                st.warning(f"No data found for Paddle Number {search_paddle}.")
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

    # Display all data with totals
    st.header("All Participant and Sales Data")
    try:
        all_data_query = """
            SELECT 
                u.paddle_number, u.name, u.phone, s.item_number, s.amount 
            FROM users AS u 
            LEFT JOIN sales AS s 
            ON u.paddle_number = s.paddle_number
        """
        all_data_df = con.sql(all_data_query).df()
        if not all_data_df.empty:
            st.dataframe(all_data_df)
            total_sales_amount = all_data_df['amount'].fillna(0).sum()
            st.write(f"**Total Amount for All Sales: ${total_sales_amount}**")
        else:
            st.warning("No data available.")
    except Exception as e:
        st.error(f"Failed to fetch all data: {e}")

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        set_page("register")
