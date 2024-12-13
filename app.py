# app.py
import duckdb
import pandas as pd
import streamlit as st

# MotherDuck token and database connection
motherduck_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sczEyMDIzQGJ5dWkuZWR1Iiwic2Vzc2lvbiI6Im9sczEyMDIzLmJ5dWkuZWR1IiwicGF0IjoiTmpYbGd3ZXlXMUJjaXY2dEpMQUl6b1ozenV2RVhPNHVoYi00YTc4VUtKTSIsInVzZXJJZCI6IjY3ZDYzMWRmLTgzMjktNDhjYi04ZjRhLTk4MWI4YTI3ODVhMiIsImlzcyI6Im1kX3BhdCIsInJlYWRPbmx5IjpmYWxzZSwidG9rZW5UeXBlIjoicmVhZF93cml0ZSIsImlhdCI6MTczMzYwNzk4NX0.cesuoNv2A4wTfW7j7z2grEutIkVnLyRgrv7VYzP_RBE'  # Replace with your valid token
con = duckdb.connect(f"md:TestDB?motherduck_token={motherduck_token}")

# Ensure the required tables exist
try:
    # Create 'roster' table
    con.sql("""
        CREATE TABLE IF NOT EXISTS roster (
            id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT
        )
    """)

    # Create 'bid' table
    con.sql("""
        CREATE TABLE IF NOT EXISTS bid (
            id TEXT,
            item_id TEXT,
            bid INT
        )
    """)
except Exception as e:
    st.error(f"Error creating tables: {e}")

# Navigation logic using session state
if "page" not in st.session_state:
    st.session_state["page"] = "register"  # Default to first page
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "delete_authenticated" not in st.session_state:
    st.session_state["delete_authenticated"] = False

def set_page(page):
    st.session_state["page"] = page

def authenticate(password, for_delete=False):
    if password == "1234567":
        if for_delete:
            st.session_state["delete_authenticated"] = True
            st.success("Password correct for Delete Page")
        else:
            st.session_state["authenticated"] = True
            st.success("Password correct")
        return True
    else:
        st.error("Incorrect password. Try again.")
        return False

# First Page: Registration
if st.session_state["page"] == "register":
    st.title("Auction Participant Registration")
    id = st.text_input("ID")
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")

    if st.button("Register"):
        if id and name and phone:
            query = f"""
                INSERT INTO roster (id, name, phone)
                VALUES ('{id}', '{name}', '{phone}')
            """
            try:
                con.sql(query)
                st.success(f"Participant {name} with ID {id} has been registered successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please fill in all fields.")

    if st.button("Go to Admin Page"):
        set_page("password")

# Password Page
elif st.session_state["page"] == "password":
    st.title("Admin Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Submit"):
        if authenticate(password):
            set_page("admin")

# Admin Page
elif st.session_state["page"] == "admin" and st.session_state["authenticated"]:
    st.title("Admin Dashboard")

    # Navigation within admin
    if st.button("Go to Delete Data Page"):
        set_page("delete_password")

    # Search by ID
    st.header("Search by ID")
    search_id = st.number_input("Enter ID to Search", min_value=0, step=1)

    if st.button("Search"):
        try:
            roster_query = f"SELECT * FROM roster WHERE id = '{search_id}'"
            bid_query = f"SELECT * FROM bid WHERE id = '{search_id}'"
            roster_df = con.sql(roster_query).df()
            bid_df = con.sql(bid_query).df()

            if not roster_df.empty:
                st.write("Roster Data:")
                st.dataframe(roster_df)
            else:
                st.warning("No data found in roster table.")

            if not bid_df.empty:
                st.write("Bid Data:")
                st.dataframe(bid_df)
                total_bid = bid_df['bid'].sum()
                st.write(f"Total Bid Amount: ${total_bid}")
            else:
                st.warning("No data found in bid table.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.header("All Roster Data")
    roster_df = con.sql("SELECT * FROM roster").df()
    st.dataframe(roster_df if not roster_df.empty else pd.DataFrame(columns=["id", "name", "phone"]))

    st.header("All Bid Data")
    bid_df = con.sql("SELECT * FROM bid").df()
    st.dataframe(bid_df if not bid_df.empty else pd.DataFrame(columns=["id", "item_id", "bid"]))

    if st.button("Logout"):
        st.session_state["authenticated"] = False
        set_page("register")

# Delete Data Password Page
elif st.session_state["page"] == "delete_password":
    st.title("Delete Data - Authentication Required")
    password = st.text_input("Enter Password", type="password")
    if st.button("Submit"):
        if authenticate(password, for_delete=True):
            set_page("delete")

# Delete Data Page
elif st.session_state["page"] == "delete" and st.session_state["delete_authenticated"]:
    st.title("Delete Data")

    # Select the table to delete from
    table = st.selectbox("Select a Table", options=["roster", "bid"])

    # Show all data from the selected table
    try:
        query = f"SELECT * FROM {table}"
        data_df = con.sql(query).df()
        if not data_df.empty:
            st.dataframe(data_df)
        else:
            st.warning(f"No data available in {table} table.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    # Enter the ID to delete
    delete_id = st.text_input(f"Enter the ID to delete from {table}")

    if st.button("Delete"):
        try:
            delete_query = f"DELETE FROM {table} WHERE id = '{delete_id}'"
            con.sql(delete_query)
            st.success(f"Data with ID {delete_id} has been deleted from {table} table.")
        except Exception as e:
            st.error(f"Error deleting data: {e}")

    # Navigate back to admin
    if st.button("Back to Admin Dashboard"):
        set_page("admin")