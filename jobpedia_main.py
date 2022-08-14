import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect


# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)


# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=10)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows


def home():
        st.header('Jobpedia')
        st.caption('みんなの進路指導')
        st.write('投稿はこちら：　https://forms.gle/7wKCjNFNDQqLVKa88')

def contents(df2):
    st.title(f"{df2['jobname']}")
    st.caption(f"{df2['year']}年記載")

    st.subheader('何をする仕事か？')
    st.markdown(f"{df2['content']}")

    st.subheader('この仕事の好きなところは？')
    st.markdown(f"{df2['like']}")

    st.subheader('この仕事はどんな人に向いている？')
    st.markdown(f"{df2['recommend']}")


    st.subheader('この仕事はどんな人に向いていない？')
    st.markdown(f"{df2['discourage']}")

def main():
    sheet_url = st.secrets["private_gsheets_url"]
    wholedata = run_query(f'SELECT * FROM "{sheet_url}"')

    df = pd.DataFrame(wholedata)
    #df.reset_index()
    #print(df["category"])

    options = st.sidebar.radio('ナビゲーション', options = ['ホームへ戻る','投稿を読む'])

    st.sidebar.title('投稿を読む')

    #select level 1: job category
    jobclist = df["category"]
    jobc = st.sidebar.selectbox("職業カテゴリ:", jobclist)

    df1 = df[df["category"] == jobc]


    #select level 2: individual page
    jobnamelist = df1["jobname"]
    jobname = st.sidebar.selectbox("職業名:", jobnamelist)



    #Print page
    # import pdb;pdb.set_trace()

    df2 = df1[df1["jobname"] == jobname]


# st.write(df2["jobname"])


    if options == 'ホームへ戻る':
        home()
    else:
        contents(df2)


main()