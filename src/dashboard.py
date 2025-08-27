import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

OCEAN_COLORS = ['#40E0D0', '#1E90FF', '#20B2AA',
                '#DC143C', '#4682B4', '#008B8B', '#5F9EA0']

st.set_page_config(
    page_title="Ondoriya Dashboard",
    page_icon="🏰",
    layout="wide"
)

# Custom CSS for ocean theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #40E0D0 0%, #1E90FF 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .metric-container {
        background: rgba(64, 224, 208, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #40E0D0;
    }
    .section-header {
        color: #1E90FF;
        border-bottom: 2px solid #40E0D0;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data_from_snowflake():
    """Load data from Snowflake gold layer"""
    try:
        with snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA_GOLD'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE')
        ) as conn:
            check_columns_query = """
            SELECT * FROM gold.ondoryia LIMIT 1
            """
            possible_queries = [
                # Quoted, case-sensitive (matches your actual column names)
                """SELECT \"Region_ID\", \"Full_Name\", \"Current_Faction\", \"POPULATION_COUNT\", \"RULING_COUNT\", \"COMMON_COUNT\" FROM gold.ondoryia""",
                # Original case
                """SELECT Region_ID, Full_Name, Current_Faction, POPULATION_COUNT, RULING_COUNT, COMMON_COUNT FROM gold.ondoryia""",
                # All uppercase
                """SELECT REGION_ID, FULL_NAME, CURRENT_FACTION, POPULATION_COUNT, RULING_COUNT, COMMON_COUNT FROM gold.ondoryia""",
                # All lowercase
                """SELECT region_id, full_name, current_faction, population_count, ruling_count, common_count FROM gold.ondoryia""",
            ]
            for i, query in enumerate(possible_queries):
                try:
                    df = pd.read_sql(query, conn)
                    return df
                except Exception as query_error:
                    if i == 0:  # On first failure, show what columns exist
                        try:
                            sample_df = pd.read_sql(check_columns_query, conn)
                            st.error(
                                f"Column name mismatch. Available columns in your table: {list(sample_df.columns)}")
                        except Exception as e:
                            st.error(
                                f"Failed to fetch columns from table: {e}")
                    st.warning(f"Query attempt {i+1} failed: {query_error}")
                    continue
            raise Exception(
                "Could not find matching column names in gold.ondoryia table.")
    except Exception as e:
        st.error(f"Error connecting to Snowflake or loading data: {e}")
    return pd.DataFrame({
        'Region_ID': [101, 102, 103, 104, 105],
        'Full_Name': ['Tekvar-Tor', 'Solthera-Ara', 'Jarovin-Vash', 'Dravzek-Tor', 'Shulmar-Shun'],
        'Current_Faction': ['Praxis Directorate', 'Empyrean Synod', 'Vesperian Concord', 'Praxis Directorate', 'Factionless'],
        'POPULATION_COUNT': [7680, 8990, 7450, 14260, 670],
        'RULING_COUNT': [96, 113, 94, 179, 9],
        'COMMON_COUNT': [1793, 2107, 1752, 3361, 156]
    })


regions_data = load_data_from_snowflake()

# Banner image across 75% of the top
st.markdown(
    '''<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 30px;">
        <img src="https://img.freepik.com/premium-photo/beautiful-valley-old-medieval-fantasy-town-castle-concept-art_492154-737.jpg?semt=ais_hybrid&w=740&q=80" 
             style="width:75%; border-radius: 10px; object-fit: cover; box-shadow: 0 4px 16px rgba(30,144,255,0.15);"/>
    </div>''', unsafe_allow_html=True)

# Title below the banner
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("Ondoriya")
st.markdown("</div>", unsafe_allow_html=True)

# Calculate metrics
total_population = regions_data['POPULATION_COUNT'].sum()
faction_counts = regions_data['Current_Faction'].value_counts()
dominant_faction = faction_counts.index[0]
dominant_percentage = (faction_counts.iloc[0] / len(regions_data)) * 100

# Top metrics row
col1, col2, col3 = st.columns([2, 3, 3])

with col1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Total Population", f"{total_population:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric("Dominant Faction", dominant_faction)
    st.write(f"Controls **{dominant_percentage:.1f}%** of regions")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Population Analysis Section
st.markdown('<h2 class="section-header">Population Analysis</h2>',
            unsafe_allow_html=True)

# Bar chart: Top 5 most populated regions (full width, unique color per bar, no faction info)

# Bar chart: Top 10 most populated regions (full width, more varied blue/green shades, no faction info)
top10_populated_regions = regions_data.nlargest(10, 'POPULATION_COUNT').copy()

# Bar chart: Top 20 most populated regions (vertical, names on bars)
top20_populated_regions = regions_data.nlargest(20, 'POPULATION_COUNT').copy()
total_pop = top20_populated_regions['POPULATION_COUNT'].sum()
top20_populated_regions['PERCENT'] = (
    top20_populated_regions['POPULATION_COUNT'] / total_pop * 100).round(1)
bar_colors_20 = [
    '#0d47a1', '#1976d2', '#42a5f5', '#64b5f6', '#00bfae', '#00897b', '#43a047', '#388e3c', '#81c784', '#b2dfdb',
    '#01579b', '#0288d1', '#26c6da', '#26a69a', '#2e7d32', '#388e3c', '#689f38', '#8bc34a', '#aed581', '#b2ebf2'
]
fig_bar = px.bar(
    top20_populated_regions,
    x='Full_Name',
    y='POPULATION_COUNT',
    title="Top 20 Most Populated Regions",
    color_discrete_sequence=bar_colors_20,
    text='Full_Name'
)
fig_bar.update_traces(
    texttemplate='%{text}',
    textposition='inside',
    marker_color=bar_colors_20[:len(top20_populated_regions)]
)
fig_bar.update_layout(
    height=500,
    yaxis=dict(range=[0, 20000], dtick=5000),
    xaxis_title='Region',
    yaxis_title='Population',
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Faction Power Section
st.markdown('<h2 class="section-header">Faction Power</h2>',
            unsafe_allow_html=True)

# Calculate faction data
faction_ruling_households = regions_data.groupby(
    'Current_Faction')['RULING_COUNT'].sum().reset_index()
faction_common_households = regions_data.groupby(
    'Current_Faction')['COMMON_COUNT'].sum().reset_index()
faction_population_control = regions_data.groupby(
    'Current_Faction')['POPULATION_COUNT'].sum().reset_index()
faction_population_control['Population_Percentage'] = (
    faction_population_control['POPULATION_COUNT'] / faction_population_control['POPULATION_COUNT'].sum() * 100).round(1)

col1, col2 = st.columns(2)

with col1:
    # Ruling households by faction
    ruling_colors = ['#1565c0', '#1976d2', '#42a5f5', '#64b5f6']
    max_idx = faction_ruling_households['RULING_COUNT'].idxmax()
    total_ruling = faction_ruling_households['RULING_COUNT'].sum()
    faction_ruling_households['PERCENT'] = (
        faction_ruling_households['RULING_COUNT'] / total_ruling * 100).round(1)
    ruling_bar_colors = [
        '#e53935' if i == max_idx else ruling_colors[i % len(ruling_colors)]
        for i in range(len(faction_ruling_households))
    ]
    fig_ruling = px.bar(
        faction_ruling_households,
        x='Current_Faction',
        y='RULING_COUNT',
        title="Ruling Households by Faction",
        text='RULING_COUNT'
    )
    fig_ruling.update_traces(
        texttemplate='%{text} (%{customdata[0]}%)',
        textposition='outside',
        marker_color=ruling_bar_colors,
        customdata=faction_ruling_households[['PERCENT']].values
    )
    fig_ruling.update_layout(
        showlegend=False,
        height=500,
        yaxis=dict(range=[0, 10000], dtick=2000),
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_ruling, use_container_width=True)

with col2:
    # Common households by faction (different blues, highest is red)
    common_colors = ['#1976d2', '#42a5f5', '#64b5f6', '#00bfae']
    max_idx = faction_common_households['COMMON_COUNT'].idxmax()
    total_common = faction_common_households['COMMON_COUNT'].sum()
    faction_common_households['PERCENT'] = (
        faction_common_households['COMMON_COUNT'] / total_common * 100).round(1)
    common_bar_colors = [
        '#e53935' if i == max_idx else common_colors[i % len(common_colors)]
        for i in range(len(faction_common_households))
    ]
    fig_common = px.bar(
        faction_common_households,
        x='Current_Faction',
        y='COMMON_COUNT',
        title="Common Households by Faction",
        text='COMMON_COUNT'
    )
    fig_common.update_traces(
        texttemplate='%{text} (%{customdata[0]}%)',
        textposition='outside',
        marker_color=common_bar_colors,
        customdata=faction_common_households[['PERCENT']].values
    )
    fig_common.update_layout(
        showlegend=False,
        height=500,
        yaxis=dict(range=[0, 200000], dtick=50000),
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_common, use_container_width=True)

# Population controlled by faction (horizontal bar with percentages)
st.subheader("Population Controlled by Faction")


# Population controlled by faction (horizontal bar with percentages, highest is red, others blue/green)
pop_colors = ['#1976d2', '#42a5f5', '#64b5f6', '#00bfae']
max_idx = faction_population_control['POPULATION_COUNT'].idxmax()
pop_bar_colors = [
    '#e53935' if i == max_idx else pop_colors[i % len(pop_colors)]
    for i in range(len(faction_population_control))
]
fig_pop = px.bar(
    faction_population_control,
    x='POPULATION_COUNT',
    y='Current_Faction',
    orientation='h',
    title="Population Controlled by Each Faction",
    text='Population_Percentage'
)
fig_pop.update_traces(
    texttemplate='%{x:,} (%{text}%)',
    textposition='outside',
    marker_color=pop_bar_colors
)
fig_pop.update_layout(
    height=400,
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_pop, use_container_width=True)

# Footer
st.markdown("---")
