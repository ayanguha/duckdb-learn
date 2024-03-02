import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(layout="wide")

# Draw a title and some text to the app:
'''
# This is demo for duckdb with streamlit
'''


def prepare_data():
    con = duckdb.connect(database='car_prices.duckdb')
    qry = "CREATE OR REPLACE TABLE car_prices as SELECT * from read_csv('../data/car_prices.csv')"
    con.execute(qry)
    return con

def run_qry(connection, qry, extra_param = []):
    if extra_param:
        df = connection.execute(qry, extra_param).df()
    else:
        df = connection.execute(qry).df()
    return df


duckdb_conn = prepare_data()
make_stats_qry = '''
        SELECT make, count(*) cnt
          from car_prices
      group by make
        having count(*)>=1000
        order by 2 desc
        '''
make_stats = run_qry(duckdb_conn, make_stats_qry)

st.bar_chart(data = make_stats, x='make', y='cnt', color=None)

pricing_stats_qry = '''
        SELECT distinct upper(body) body, odometer, sellingprice
          from car_prices
          where sellingprice <= 100000 and odometer <= 100000 and make in ('Ford')
        '''
pricing_stats = run_qry(duckdb_conn, pricing_stats_qry)
make_list_qry = 'select distinct upper(make) make from car_prices order by 1'
make_list = run_qry(duckdb_conn, make_list_qry)

col1, col2 = st.columns(2)
with col1:
    st.scatter_chart(data = pricing_stats, x='odometer', y='sellingprice', color='body')

state_level_stats_qry = '''
select  year, upper(state) state, max(sellingprice) sellingprice
from car_prices
where sellingprice <= 100000 and odometer <= 100000
and upper(make) = ?
group by year, state
order by 1,2
'''


with col2:
    make = st.selectbox("Choose a make", make_list)
    st.write('You selected:', make)
    state_level_stats = run_qry(duckdb_conn, state_level_stats_qry, extra_param = [make])

    fig = px.choropleth(state_level_stats,
                        color="sellingprice",
                        locations="state",
                        locationmode="USA-states",
                        scope="usa",
                        animation_frame = 'year',
                        color_continuous_scale=px.colors.sequential.Plasma
                   )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(figure_or_data = fig)
