import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def app1():
    st.title('App 1')
    st.write('This is the first app')

def app2():
    st.title('App 2')
    st.write('This is the second app')

# Main page

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
# Add two buttons side by side to choose the app
col1, col2 = st.columns(2) # Create two columns
if col1.button('Ask Any Query'):
    switch_page("App1")
if col2.button('Classwise Query'):
    switch_page("App2")
