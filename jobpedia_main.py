import streamlit as st
import pandas as pd
pd.set_option("max_colwidth", 200)
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

def series_to_string(series):
    if series.values[0] == None :
        return "無回答です"
    return f"{series.to_string(index=False)}".replace("\\n", "  \n") # it doesnt work without two spaces (i dont know why)

def home():
   
    st.markdown("  ")
    st.markdown("## Home")
    st.markdown("### ハロワクとは？")
    st.markdown("「15歳が、世の中にどんな仕事があるか手にとるように知ることのできる場」を目指しています。キャリアに迷う大人にもおすすめです。")
    st.markdown("  ")
    st.markdown("#### 新しい投稿を追加する↓  ")
    st.markdown("https://forms.gle/7wKCjNFNDQqLVKa88")
    st.markdown("  ")
    st.markdown("#### お問合せはこちら↓")
    st.markdown("inekarieアットマークgmail.com")

def contents(df2):
    st.title(f"{df2['jobname'].to_string(index=False)}")
    st.caption(f"{df2['year'].to_string(index=False)}年記載")

    st.subheader('何をする仕事か？')
    st.markdown( series_to_string( df2['content'] ) )

    st.subheader('この仕事の好きなところは？')
    st.markdown( series_to_string ( df2['like'] )) 

    st.subheader('この仕事はどんな人に向いている？')
    st.markdown( series_to_string( df2['recommend'] ) )

    st.subheader('この仕事はどんな人に向いていない？')
    st.markdown( series_to_string ( df2['discourage'] )) 

def main():
    st.markdown("# ハローワクワク")
    st.markdown("#### みんなの進路指導")
    options = st.radio('', options = ['ホームへ戻る','投稿を読む'])
    st.markdown("    ")
  

    if options == 'ホームへ戻る':
        home()
    else:
        sheet_url = st.secrets["private_gsheets_url"]
        wholedata = run_query(f'SELECT * FROM "{sheet_url}"')

        df_ = pd.DataFrame(wholedata)
        df = df_.set_axis(['timestamp','year','jobname','category','content','like','recommend','discourage'], axis='columns')
        
        #select level 1: job category
        jobclist = df["category"]
        jobclist = jobclist[~jobclist.duplicated()] 
        jobclist = jobclist.sort_values()
        
        jobc = st.selectbox("職業カテゴリ:", jobclist)
        df1 = df[df["category"] == jobc]

        #select level 2: individual page
        jobnamelist = df1["jobname"]
        jobnamelist = jobnamelist.sort_values()

        jobname = st.selectbox("職業名:", jobnamelist)

        df2 = df1[df1["jobname"] == jobname]
        contents(df2)



main()