import duckdb
import streamlit as st
import pandas as pd

# Your MotherDuck token
motherduck_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im9sczEyMDIzQGJ5dWkuZWR1Iiwic2Vzc2lvbiI6Im9sczEyMDIzLmJ5dWkuZWR1IiwicGF0IjoiTmpYbGd3ZXlXMUJjaXY2dEpMQUl6b1ozenV2RVhPNHVoYi00YTc4VUtKTSIsInVzZXJJZCI6IjY3ZDYzMWRmLTgzMjktNDhjYi04ZjRhLTk4MWI4YTI3ODVhMiIsImlzcyI6Im1kX3BhdCIsInJlYWRPbmx5IjpmYWxzZSwidG9rZW5UeXBlIjoicmVhZF93cml0ZSIsImlhdCI6MTczMzYwNzk4NX0.cesuoNv2A4wTfW7j7z2grEutIkVnLyRgrv7VYzP_RBE'

# Connect to the MotherDuck database using the token
con = duckdb.connect(f"md:TestDB?motherduck_token={motherduck_token}")

# Execute a SQL query to fetch data
result = con.sql('SELECT * FROM roster LIMIT 10').fetchall()  # Modify query as needed

# Convert the result into a pandas DataFrame for Streamlit display
df = pd.DataFrame(result, columns=['column1', 'column2', 'column3'])  # Replace with actual column names

# Use Streamlit to display the DataFrame
st.write("Data from MotherDuck:")
st.write(df)
