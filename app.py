# app.py
import duckdb
import pandas as pd
import streamlit as st

# MotherDuck token and database connection
motherduck_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sczEyMDIzQGJ5dWkuZWR1Iiwic2Vzc2lvbiI6Im9sczEyMDIzLmJ5dWkuZWR1IiwicGF0IjoiTmpYbGd3ZXlXMUJjaXY2dEpMQUl6b1ozenV2RVhPNHVoYi00YTc4VUtKTSIsInVzZXJJZCI6IjY3ZDYzMWRmLTgzMjktNDhjYi04ZjRhLTk4MWI4YTI3ODVhMiIsImlzcyI6Im1kX3BhdCIsInJlYWRPbmx5IjpmYWxzZSwidG9rZW5UeXBlIjoicmVhZF93cml0ZSIsImlhdCI6MTczMzYwNzk4NX0.cesuoNv2A4wTfW7j7z2grEutIkVnLyRgrv7VYzP_RBE'  # Replace with your valid token
con = duckdb.connect(f"md:TestDB?motherduck_token={motherduck_token}")

# Ensure the required tables exist
try:
    # Create 'roster' table (first page)
    con.sql("""
        CREATE TABLE IF NOT EXISTS roster (
            id TEXT PRIMARY KEY,  -- Ensure 'id' is the primary key
            name TEXT,
            phone TEXT
        )
    """)

    # Create 'bid' table (second page)
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

def set_page(page):
    st.session_state["page"] = page

def authenticate(password):
    if password == "1234567":
        st.session_state["authenticated"] = True
        st.success("Password correct")
        set_page("admin")
    else:
        st.error("Try again")

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

    # Button to go to the password-protected admin page
    if st.button("Go to Admin Page"):
        set_page("password")

# Password Page
elif st.session_state["page"] == "password":
    st.title("Admin Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Submit"):
        authenticate(password)

# Admin Page (second page, for displaying data)
elif st.session_state["page"] == "admin" and st.session_state["authenticated"]:
    st.title("Admin Dashboard")

    # Search by ID using number_input()
    st.header("Search by ID")
    search_id = st.number_input("Enter ID to Search", min_value=0, step=1)

    if st.button("Search"):
        try:
            # Search data from 'roster' table based on ID
            roster_query = f"""
                SELECT * FROM roster WHERE id = '{search_id}'
            """
            roster_df = con.sql(roster_query).df()

            # Search data from 'bid' table based on ID
            bid_query = f"""
                SELECT * FROM bids WHERE id = '{search_id}'
            """
            bid_df = con.sql(bid_query).df()

            # Display results for 'roster'
            if not roster_df.empty:
                st.write(f"Roster Data for ID: {search_id}")
                st.dataframe(roster_df)
            else:
                st.warning(f"No data found for ID: {search_id} in roster table.")

            # Display results for 'bid'
            if not bid_df.empty:
                st.write(f"Bid Data for ID: {search_id}")
                st.dataframe(bid_df)
                total_bid_amount = bid_df['bid'].sum()  # Total amount in bids
                st.write(f"**Total Bid Amount for ID {search_id}: ${total_bid_amount}**")
            else:
                st.warning(f"No data found for ID: {search_id} in bid table.")

        except Exception as e:
            st.error(f"Error fetching data: {e}")

    # Display all 'roster' data if no search is performed
    st.header("All Roster Data")
    try:
        all_roster_query = "SELECT * FROM roster"
        all_roster_df = con.sql(all_roster_query).df()
        if not all_roster_df.empty:
            st.dataframe(all_roster_df)
        else:
            st.write("No data available in the roster.")
            st.dataframe(pd.DataFrame(columns=["id", "name", "phone"]))  # Empty DataFrame if no data
    except Exception as e:
        st.error(f"Failed to fetch all roster data: {e}")

    # Display all 'bid' data if no search is performed
    st.header("All Bid Data")
    try:
        all_bid_query = "SELECT * FROM bids"
        all_bid_df = con.sql(all_bid_query).df()
        if not all_bid_df.empty:
            st.dataframe(all_bid_df)
            total_bid_amount_all = all_bid_df['bid'].sum()  # Total amount in bids for all records
            st.write(f"**Total Bid Amount for All: ${total_bid_amount_all}**")
        else:
            st.write("No data available in the bid table.")
            st.dataframe(pd.DataFrame(columns=["id", "item_id", "bid"]))  # Empty DataFrame if no data
    except Exception as e:
        st.error(f"Failed to fetch all bid data: {e}")

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        set_page("register")