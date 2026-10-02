import streamlit as st
from streamlit_option_menu import option_menu    
import pandas as pd
import pymysql
import time
import numpy as np


st.set_page_config(
    page_title="NHL Analytics Hub",
    page_icon="🏒",
    layout="wide"
)

#connenction string
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='nhl_analytics'
)

cursor = conn.cursor()

with st.sidebar:
        selected = option_menu("NHL ANALYTICS HUB", ["Home","Team Comparison","Queries","Query Playground","League Leaders","Standings","Player Details"], 
            icons=['house','bar-chart','database','terminal','trophy-fill','trophy',"person"], menu_icon="cast", default_index=1)
        selected
if selected == "Home":
        
        c1,c2=st.columns(2)
        with c1:
            st.image("Screenshot 2026-09-23 170755.png",width=180)
        with c2:
            st.title("🏒 NHL ANALYTICS HUB")
        st.divider()
        st.write("API-driven hockey data pipeline with SQL analysis and Streamlit dashboard")   
        cursor.execute("SELECT COUNT(*) FROM teams")
        total_teams = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM players")
        total_players = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM games")
        total_games = cursor.fetchone()[0]
        cursor.execute("""
            SELECT COALESCE(SUM(home_score) + SUM(away_score), 0)
            FROM games
        """)
        total_goals = cursor.fetchone()[0]
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🏒 Total Teams",
                total_teams
            )

        with col2:
            st.metric(
                "👤 Total Players",
                total_players
            )

        with col3:
            st.metric(
                "🏆 Total Games",
                total_games
            )
        with col4:
            st.metric(
                "🥅 Total Goals Scored",
                total_goals
            )

        st.divider()

        c1,c2,c3=st.columns(3)

        cursor.execute("""
            SELECT
                p.first_name,
                p.last_name,
                s.goals
            FROM players p
            JOIN skater_season_stats s
                ON p.player_id = s.player_id
            ORDER BY s.goals DESC
            LIMIT 1
        """)

        top_scorer = cursor.fetchone()

        top_scorer_name = (
        top_scorer[0] + " " + top_scorer[1]
        )

        top_scorer_goals = top_scorer[2]
        with c1:
            st.metric(
            "⭐ Top Scorer",
            top_scorer_name,
            f"{top_scorer_goals} goals"
        )

        cursor.execute("""
            SELECT
                p.first_name,
                p.last_name,
                g.save_pct
            FROM players p
            JOIN goalie_season_stats g
                ON p.player_id = g.player_id
            WHERE g.save_pct IS NOT NULL
            ORDER BY g.save_pct DESC
            LIMIT 1
        """)

        best_save = cursor.fetchone()

        best_goalie_name = best_save[0] + " " + best_save[1]
        best_save_percentage = best_save[2]
        with c2:
            st.metric(
                "🧤 Best Save %",
                best_goalie_name,
                f"{best_save_percentage:.3f}"
            )

        cursor.execute("""
                SELECT
                t.team_name,
                s.points
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            ORDER BY s.points DESC
            LIMIT 1
        """)

        league_leader = cursor.fetchone()

        leader_name = league_leader[0]
        leader_points = league_leader[1]

        with c3:
            st.metric(
                "🏆 League Leader",
                leader_name,
                f"{leader_points} pts"
        )
            
if selected == "Queries":
        st.title("SQL Queries") 
        option = st.selectbox(
            "Select Query to run",
            ("1. Which team has scored the most total goals this season?",
            "2. Which teams have more than 30 wins?", 
            "3. How many teams are there in each division?",
            "4. Which team has the highest number of points?",
            "5. What is the average height of players in the database?",
            "6. List all players along with their first name, last name, position, and jersey number.",
            "7. Display the top 10 teams according to their points.",
            "8. Which teams have the highest positive goal difference?",
            "9. Which players have scored the most goals during the season?",
            "10. For each team, compare how many games they won at home versus how many they won away.", 
            "11. Display each team's name along with its games played, wins, losses, and points.", 
            "12. How many players belong to each NHL team? "), 
        )
        if option=="1. Which team has scored the most total goals this season?":
            df=pd.read_sql_query("SELECT t.team_name, s.goals_for FROM teams t JOIN standings s ON t.team_id = s.team_id ORDER BY s.goals_for DESC LIMIT 1;",conn) 
            st.dataframe(df) 
        elif option=="2. Which teams have more than 30 wins?":
            df=pd.read_sql_query("SELECT t.team_name, s.wins FROM teams t JOIN standings s ON t.team_id = s.team_id WHERE s.wins > 30;",conn) 
            st.dataframe(df) 
        elif option=="3. How many teams are there in each division?":
            df=pd.read_sql_query("SELECT division_name, COUNT(*) AS total_teams FROM teams GROUP BY division_name;",conn)
            st.dataframe(df) 
        elif option=="4. Which team has the highest number of points?":
            df=pd.read_sql_query("SELECT t.team_name, s.points FROM teams t JOIN standings s ON t.team_id = s.team_id ORDER BY s.points DESC LIMIT 1;",conn)
            st.dataframe(df) 
        elif option.startswith("5."):
            df = pd.read_sql_query("SELECT AVG(height_cm) AS average_height FROM players;", conn)
            st.dataframe(df)
        elif option=="6. List all players along with their first name, last name, position, and jersey number.":
            df=pd.read_sql_query("SELECT first_name, last_name, position, jersey_number FROM players;",conn)
            st.dataframe(df) 
        elif option=="7. Display the top 10 teams according to their points.":
            df=pd.read_sql_query("SELECT t.team_name, s.points FROM teams t JOIN standings s ON t.team_id = s.team_id ORDER BY s.points DESC LIMIT 10;",conn)
            st.dataframe(df) 
        elif option=="8. Which teams have the highest positive goal difference?":
            df=pd.read_sql_query("SELECT t.team_name,(s.goals_for - s.goals_against) AS goal_difference FROM teams t JOIN standings s ON t.team_id = s.team_id ORDER BY goal_difference DESC;",conn)
            st.dataframe(df) 
        elif option=="9. Which players have scored the most goals during the season?":
            df=pd.read_sql_query("SELECT p.first_name, p.last_name, s.goals FROM players p JOIN skater_season_stats s ON p.player_id = s.player_id ORDER BY s.goals DESC LIMIT 10;",conn)
            st.dataframe(df) 
        elif option == "10. For each team, compare how many games they won at home versus how many they won away.":
            df = pd.read_sql_query("SELECT t.team_name, s.home_wins, s.road_wins FROM teams t JOIN standings s ON t.team_id = s.team_id;", conn)
            st.dataframe(df)
        elif option=="11. Display each team's name along with its games played, wins, losses, and points.":
            df=pd.read_sql_query("SELECT t.team_name, s.games_played, s.wins, s.losses, s.points FROM teams t JOIN standings s ON t.team_id = s.team_id;",conn)
            st.dataframe(df) 
        elif option.startswith("12."):
            df = pd.read_sql_query("SELECT t.team_name, COUNT(p.player_id) AS player_count FROM teams t LEFT JOIN players p ON t.team_id = p.team_id GROUP BY t.team_id, t.team_name;", conn)
            st.dataframe(df)
if selected == "Standings":

    st.title("Standings")
    st.subheader("Conference")

    cursor.execute("""
        SELECT DISTINCT conf_name
        FROM teams
        WHERE conf_name IS NOT NULL
        ORDER BY conf_name
    """)

    conference_data = cursor.fetchall()

    conferences = ["All"]

    for row in conference_data:
        conferences.append(row[0])

    selected_conference = st.selectbox(
        "Conference",
        conferences
    )

    if selected_conference == "All":

        cursor.execute("""
            SELECT
                t.team_name,
                t.conf_name,
                t.division_name,
                s.wins,
                s.losses,
                s.points,
                s.goals_for,
                s.goals_against
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            ORDER BY s.points DESC
        """)

    else:

        cursor.execute("""
            SELECT
                t.team_name,
                t.conf_name,
                t.division_name,
                s.wins,
                s.losses,
                s.points,
                s.goals_for,
                s.goals_against
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            WHERE t.conf_name = %s
            ORDER BY s.points DESC
        """, (selected_conference,))
    data = cursor.fetchall()
    df = pd.DataFrame(
            data,
            columns=[
                "Team",
                "Conference",
                "Division",
                "Wins",
                "Losses",
                "Points",
                "Goals For",
                "Goals Against"
            ]
        )
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
if selected == "Query Playground":
    st.title("🧮 SQL Query Playground")

    st.write(
            "Write and execute SQL queries directly on the NHL database."
        )
    query = st.text_area(
        "Write your SQL query:",
        height=180,
        placeholder="""Example:
SELECT *
FROM teams
LIMIT 10;"""
    )
    if st.button("▶ Run Query"):

        if query.strip() == "":
            st.warning("Please enter a SQL query.")

        else:
            try:
                cursor.execute(query)

            # Get column names
                columns = [desc[0] for desc in cursor.description]

            # Get result
                result = cursor.fetchall()
            # Convert to DataFrame
                df = pd.DataFrame(
                    result,
                    columns=columns
                )

                st.success(
                    f"Query executed successfully — {len(df)} rows returned."
                )

            # Result
                st.subheader("📊 Query Result")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            except Exception as e:
                st.error(f"SQL Error: {e}")

if selected == "Team Comparison":

    st.title("⚔️🤠 Team Comparison")
    st.write(
        "Compare NHL teams using their standings and performance statistics."
    )

    # Fetch team names and their standings from MySQL
    cursor.execute("""
        SELECT
            t.team_id,
            t.team_name,
            s.games_played,
            s.wins,
            s.losses,
            s.points,
            s.goals_for,
            s.goals_against,
            s.home_wins,
            s.road_wins
        FROM teams t
        JOIN standings s
            ON t.team_id = s.team_id
        ORDER BY t.team_name
    """)

    rows = cursor.fetchall()

    columns = [
        "Team ID",
        "Team",
        "Games Played",
        "Wins",
        "Losses",
        "Points",
        "Goals For",
        "Goals Against",
        "Home Wins",
        "Away Wins"
    ]

    teams_df = pd.DataFrame(rows, columns=columns)

    if teams_df.empty:
        st.warning("No team standings were found in the database.")

    else:
        # Select two teams
        team_names = teams_df["Team"].tolist()

        col1, col2 = st.columns(2)

        with col1:
            team1 = st.selectbox(
                "Select First Team",
                team_names,
                index=0
            )

        # Prevent selecting the same team twice
        other_teams = [
            name for name in team_names
            if name != team1
        ]

        with col2:
            team2 = st.selectbox(
                "Select Second Team",
                other_teams,
                index=0
            )

        # Get the selected teams' data
        team1_data = teams_df[
            teams_df["Team"] == team1
        ].iloc[0]

        team2_data = teams_df[
            teams_df["Team"] == team2
        ].iloc[0]

        st.divider()

        # Team headings
        left, right = st.columns(2)

        with left:
            st.subheader(f"🏒 {team1}")

        with right:
            st.subheader(f"🏒 {team2}")

        # Compare key metrics
        metrics = [
            ("Games Played", "Games Played"),
            ("Wins", "Wins"),
            ("Losses", "Losses"),
            ("Points", "Points"),
            ("Goals Scored", "Goals For"),
            ("Goals Conceded", "Goals Against"),
            ("Home Wins", "Home Wins"),
            ("Away Wins", "Away Wins")
        ]

        st.subheader("📊 Head-to-Head Statistics")

        for label, column in metrics:
            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    label,
                    int(team1_data[column])
                    if pd.notna(team1_data[column])
                    else 0
                )

            with c2:
                st.metric(
                    label,
                    int(team2_data[column])
                    if pd.notna(team2_data[column])
                    else 0
                )

        st.divider()

        # Goal difference comparison
        st.subheader("🥅 Goal Difference")

        comparison_df = pd.DataFrame({
            "Team": [team1, team2],
            "Goals For": [
                team1_data["Goals For"],
                team2_data["Goals For"]
            ],
            "Goals Against": [
                team1_data["Goals Against"],
                team2_data["Goals Against"]
            ]
        })

        comparison_df["Goal Difference"] = (
            comparison_df["Goals For"]
            - comparison_df["Goals Against"]
        )

        st.bar_chart(
            comparison_df.set_index("Team")[
                ["Goals For", "Goals Against"]
            ]
        )

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )
if selected == "League Leaders":

    st.title("🏅 League Leaders")
    st.write(
        "Top-performing players, goalies and teams based on NHL statistics."
    )
    st.subheader("Top Scorers")

    cursor.execute("""
        SELECT
            CONCAT(p.first_name, ' ', p.last_name) AS player,
            s.goals
        FROM players p
        JOIN skater_season_stats s
            ON p.player_id = s.player_id
        ORDER BY s.goals DESC
        LIMIT 10
    """)

    scorer_data = cursor.fetchall()

    scorer_df = pd.DataFrame(
        scorer_data,
        columns=["Player", "Goals"]
    )

    st.dataframe(
        scorer_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Team Points Leaders")

    cursor.execute("""
        SELECT
            t.team_name AS Team,
            s.points AS Points
        FROM teams t
        JOIN standings s
            ON t.team_id = s.team_id
        ORDER BY s.points DESC
        LIMIT 10
    """)

    team_data = cursor.fetchall()

    team_df = pd.DataFrame(
        team_data,
        columns=["Team", "Points"]
    )

    st.dataframe(
        team_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Goalie Leaders")

    cursor.execute("""
        SELECT
            CONCAT(p.first_name, ' ', p.last_name) AS Goalie,
            g.save_pct,
            g.saves,
            g.shutouts
        FROM players p
        JOIN goalie_season_stats g
            ON p.player_id = g.player_id
        WHERE g.save_pct IS NOT NULL
        ORDER BY g.save_pct DESC
        LIMIT 10
    """)

    goalie_data = cursor.fetchall()

    goalie_df = pd.DataFrame(
        goalie_data,
        columns=[
            "Goalie",
            "Save %",
            "Saves",
            "Shutouts"
        ]
    )

    # Convert decimal save percentage to percentage
    goalie_df["Save %"] = goalie_df["Save %"] * 100

    st.dataframe(
        goalie_df,
        use_container_width=True,
        hide_index=True
    )
if selected == "Player Details":

    st.title("👤 Player Details")

    st.write(
        "Search and explore detailed information about NHL players."
    )

    # Get players from database
    cursor.execute("""
        SELECT
            p.player_id,
            CONCAT(p.first_name, ' ', p.last_name) AS player_name
        FROM players p
        ORDER BY player_name
    """)

    player_data = cursor.fetchall()

    if not player_data:

        st.warning("No players found in the database.")

    else:

        # Create player dictionary
        player_options = {
            row[1]: row[0]
            for row in player_data
        }

        # Player selection
        selected_player = st.selectbox(
            "🔎 Select Player",
            list(player_options.keys())
        )

        selected_player_id = player_options[selected_player]

        cursor.execute("""
            SELECT
                p.first_name,
                p.last_name,
                t.team_name,
                p.position,
                p.jersey_number,
                p.birth_date,
                p.birth_country,
                p.height_cm,
                p.weight_kg,
                p.shoots_catches
            FROM players p
            LEFT JOIN teams t
                ON p.team_id = t.team_id
            WHERE p.player_id = %s
        """, (selected_player_id,))

        player = cursor.fetchone()

        if player:

            st.subheader(
                f"🏒 {player[0]} {player[1]}"
            )

            # Basic information
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "🏒 Team",
                    player[2] if player[2] else "N/A"
                )

            with col2:
                st.metric(
                    "Position",
                    player[3] if player[3] else "N/A"
                )

            with col3:
                st.metric(
                    "Jersey",
                    player[4] if player[4] else "N/A"
                )

            with col4:
                st.metric(
                    "Shoots/Catches",
                    player[9] if player[9] else "N/A"
                )

            st.divider()

            # Physical details
            st.subheader("📋 Player Information")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write("**Birth Date**")
                st.write(player[5] if player[5] else "N/A")

            with col2:
                st.write("**Birth Country**")
                st.write(player[6] if player[6] else "N/A")

            with col3:
                st.write("**Height**")
                st.write(
                    f"{player[7]} cm"
                    if player[7]
                    else "N/A"
                )

            with col4:
                st.write("**Weight**")
                st.write(
                    f"{player[8]} kg"
                    if player[8]
                    else "N/A"
                )

        st.divider()

        cursor.execute("""
            SELECT
                season,
                games_played,
                goals
            FROM skater_season_stats
            WHERE player_id = %s
            ORDER BY season DESC
        """, (selected_player_id,))

        skater_stats = cursor.fetchall()

        if skater_stats:

            st.subheader("Season Statistics")

            skater_df = pd.DataFrame(
                skater_stats,
                columns=[
                    "Season",
                    "Games Played",
                    "Goals"
                ]
            )

            st.dataframe(
                skater_df,
                use_container_width=True,
                hide_index=True
            )

        cursor.execute("""
            SELECT
                season,
                games_played,
                wins,
                losses,
                save_pct,
                goals_against_avg,
                shutouts,
                saves
            FROM goalie_season_stats
            WHERE player_id = %s
            ORDER BY season DESC
        """, (selected_player_id,))

        goalie_stats = cursor.fetchall()

        if goalie_stats:

            st.subheader("Goalie Statistics")

            goalie_df = pd.DataFrame(
                goalie_stats,
                columns=[
                    "Season",
                    "Games Played",
                    "Wins",
                    "Losses",
                    "Save %",
                    "GAA",
                    "Shutouts",
                    "Saves"
                ]
            )

            goalie_df["Save %"] = (
                goalie_df["Save %"] * 100
            )

            st.dataframe(
                goalie_df,
                use_container_width=True,
                hide_index=True
            )
            

