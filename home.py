import streamlit as st
import pandas as pd

import io
#from streamlit_extras.switch_page_button import switch_page
if "load_state" not in st.session_state:
    st.session_state.load_state=False
# Set the initial sidebar state to collapsed
#st.set_page_config(initial_sidebar_state='collapsed')

# Hide the Streamlit style for the sidebar

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
def authenticate_user(name, school):
    user_info_bytes = db.storage.binary.get('user_info1.csv')
    if user_info_bytes is None:
        return False
    
    # Load user_info dataframe from the CSV bytes
    user_info_df = pd.read_csv(io.StringIO(user_info_bytes.decode()))
    
    # Check if the given email and password match any row in the user_info dataframe
    matching_rows = user_info_df[(user_info_df['name'] == name) & (user_info_df['school'] == school)]
    
    return not matching_rows.empty
# Registration form
name = st.text_input('Enter Student Name')
classes = st.text_input('Enter your class')
school = st.text_input('Enter School name')
Rollno=st.text_input("Enter Phone number")
emailid=st.text_input("Enter email id")
if st.button('Register'):
    if not name or not classes or not school or not Rollno or not emailid:
        st.error("Please Fill all the fields")
    else:
        user_info = {
            'name': [name],
            'class': [classes],
            'school': [school],
            'RollNo': [Rollno],
            "emailid" : [emailid]
            }
        df_user_info = pd.DataFrame(user_info)
        df_user_info.to_csv('user_info1.csv', index=False)
        with open('user_info1.csv', 'rb') as f:
                csv_bytes = f.read()
                db.storage.binary.put('user_info1.csv', csv_bytes)
        switch_page("Switch Page")
        login=st.checkbox("Go to login page")
if st.button("Login here") or st.session_state.load_state:
            st.session_state.load_state=True
            name = st.text_input("Name")
            school = st.text_input("school")
            if st.button("Login"):
                if authenticate_user(name, school):
                    st.success("Login Successful!")
                    switch_page("Switch Page")
                else:
                    st.error("Invalid Credentials")

    