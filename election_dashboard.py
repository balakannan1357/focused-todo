import pandas as pd
import streamlit as st
import altair as alt

DATA_PATH = "data/tn_elections.csv"


def load_data() -> pd.DataFrame:
    """Load and standardize Tamil Nadu election results."""
    df = pd.read_csv(DATA_PATH)
    # Normalise column names
    df.columns = [c.strip() for c in df.columns]
    rename_map = {}
    if "AC_NAME" in df.columns:
        rename_map["AC_NAME"] = "Constituency"
    if "Total Votes" in df.columns:
        rename_map["Total Votes"] = "Votes"
    if "Candidate Name" in df.columns:
        rename_map["Candidate Name"] = "Candidate"
    if "Position" in df.columns:
        rename_map["Position"] = "Position"
    df = df.rename(columns=rename_map)

    if "Votes" in df.columns:
        df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce")
    if "Position" in df.columns:
        df["Winner"] = df["Position"].astype(str) == "1"
    else:
        df["Winner"] = df.groupby(["Year", "Constituency"])["Votes"].transform(
            lambda x: x == x.max()
        )

    df["VoteShare"] = df.groupby(["Year", "Constituency"])["Votes"].transform(
        lambda x: x / x.sum()
    )

    return df

def main():
    st.title("Tamil Nadu Election Dashboard")
    st.write("Explore constituency-level results and party performance")

    df = load_data()
    years = sorted(df['Year'].unique())
    parties = sorted(df['Party'].unique())
    constituencies = sorted(df['Constituency'].unique())

    st.sidebar.header("Filters")
    year_filter = st.sidebar.multiselect("Year", years, default=years)
    party_filter = st.sidebar.multiselect("Party", parties, default=parties)
    constituency_filter = st.sidebar.multiselect(
        "Constituency", constituencies, default=constituencies)

    margin_available = "Margin" in df.columns
    close_toggle = False
    if margin_available:
        close_toggle = st.sidebar.checkbox("Show close contests (margin < 5000)")

    filtered = df[df['Year'].isin(year_filter) & df['Party'].isin(party_filter) &
                  df['Constituency'].isin(constituency_filter)]
    if margin_available and close_toggle:
        filtered = filtered[pd.to_numeric(filtered['Margin'], errors='coerce') < 5000]

    st.subheader("Vote Share by Party over Time")
    vote_share = filtered.groupby(['Year', 'Party'])['VoteShare'].mean().reset_index()
    chart = alt.Chart(vote_share).mark_line(point=True).encode(
        x='Year:O',
        y=alt.Y('VoteShare:Q', axis=alt.Axis(format='%')),
        color='Party'
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Seat Wins by Party")
    seats = filtered[filtered['Winner']].groupby(['Year', 'Party']).size().reset_index(name='Seats')
    bar = alt.Chart(seats).mark_bar().encode(
        x='Year:O',
        y='Seats:Q',
        color='Party'
    )
    st.altair_chart(bar, use_container_width=True)

    if 'Turnout' in df.columns:
        st.subheader("Voter Turnout by Constituency")
        turnout = filtered.groupby(['Year', 'Constituency'])['Turnout'].mean().reset_index()
        turnout_chart = alt.Chart(turnout).mark_bar().encode(
            x='Constituency',
            y=alt.Y('Turnout:Q', axis=alt.Axis(format='%')),
            color='Year:O'
        )
        st.altair_chart(turnout_chart, use_container_width=True)

    st.subheader("Simple 2026 Projection")
    latest = df[df['Year'] == df['Year'].max()]
    projection = latest.groupby('Party')['VoteShare'].mean().reset_index()
    projection['ProjectedVoteShare'] = projection['VoteShare'] * 1.02
    st.write(projection[['Party', 'ProjectedVoteShare']])

    st.info("Map visualization and advanced prediction models can be incorporated with larger datasets.")

if __name__ == "__main__":
    main()
