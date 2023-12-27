import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd


# Load exixsting data from 'players.xlsx' or create a new DataFrame
try:
     players = pd.read_excel('players.xlsx')
except FileNotFoundError:
     players = pd.DataFrame()

# Load exixsting data from 'players_teams.xlsx' or create a new DataFrame
try:
    players_teams = pd.read_excel('players_teams.xlsx')
except FileNotFoundError:
    players_teams = pd.DataFrame()

lock = threading.Lock()


def extract_teams(link, leagueName):
    # HTTP request
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract teams in the league
        teams_table = soup.find_all("table", {"class": "taula_estil sortable taula_classificacio"})[0]
        teams_rows = teams_table.find_all("tr")[1:]

        teams_data = []

        teams_params = [(team.select("td")[3].select("a")[0].text, team["data-ideq"]) for team in teams_rows]

        # Create the threads
        threads = [threading.Thread(target=extract_team, args=(team,)) for team in teams_params]

        # Start the threads
        for thread in threads:
            thread.start()

        # Wait for threads termination
        for thread in threads:
            thread.join()

        #
        for team in teams_rows:

            teamName = team.select("td")[3].select("a")[0].text
            teamId = team["data-ideq"]
            teams_data.append([teamId, teamName, leagueName])

        # Load existing data from 'teams.xlsx' or create a new DataFrame
        try:
            df = pd.read_excel('teams.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame()

        # Create a dataframe from teams_data
        teams_df = pd.DataFrame(teams_data, columns=["teamId", "teamName", "leagueName"])

        # Join df with teams_df, dropping duplicates according to teamId
        df = pd.concat([df, teams_df], ignore_index=True).drop_duplicates(subset=["teamId"])

        # Export the updated DataFrame in 'teams.xlsx'
        df.to_excel('teams.xlsx', index=False)

    else:
        print("HTTP Error. Code:", response.status_code)


def extract_team(x):

    teamName= x[0]
    teamId= x[1]

    print(f"Working on {teamName}...")
    # Create empty DataFrame for team data and team-player relationships
    all_squad_data = pd.DataFrame()
    team_relations_data = pd.DataFrame()

    # Loop seasons: 2000-01 to 2023-24
    for season in range(2000, 2024):
        # URL template for current season
        url = f"https://www.bdfutbol.com/en/t/t{season}-{(season + 1) % 100:02d}{teamId}.html?t=plantilla"

        # HTTP request
        response = requests.get(url)

        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract player data and player-team relation
            players_data = []
            players_relation = []
            table1 = soup.find_all("table", {"class": "taula_estil sortable"})[0]
            rows = table1.find_all("tr")[1:]

            for player_row in rows:
                player_info = player_row.select('td')

                try:
                    player_displayName = player_info[3].select("a")[0].select("span")[0].text
                    player_fullName = player_info[3].select("a")[0].select("span")[1].text
                    player_nation = player_info[2].select("div")[0]["class"][1]
                    player_birthDate = player_info[4].text
                    player_link = "https://www.bdfutbol.com/en" + player_info[3].select("a")[0]["href"][2:]
                    player_data = [player_displayName, player_fullName, player_nation, player_birthDate, player_link]
                    player_team_relation = [player_fullName, player_birthDate, teamId]

                    players_relation.append(player_team_relation)
                    players_data.append(player_data)
                except:
                    print("Player data are incomplete")

            # Create two DataFrame with current season data
            columns = ['displayName', 'fullName', 'nation', 'birthDate', 'link']
            players_df = pd.DataFrame(players_data, columns=columns)
            player_relation_df = pd.DataFrame(players_relation, columns=["fullName", "birthDate", "teamId"])

            # Join current season DataFram with the team general DataFrame
            all_squad_data = pd.concat([all_squad_data, players_df], ignore_index=True).drop_duplicates(
                subset=["fullName", "birthDate"])
            team_relations_data = pd.concat([team_relations_data, player_relation_df],
                                            ignore_index=True).drop_duplicates(subset=["fullName", "birthDate"])

        else:
            print(
                f"HTTP error for season {season}-{season + 1}. Error code: {response.status_code}. {teamName} may not have participated in the competition in the current season")

    # Acquire lock and update global DataFrame
    with lock:

        # Join DataFrame and remove duplicates
        global players
        players = pd.concat([players, all_squad_data], ignore_index=True).drop_duplicates(subset=["fullName", "birthDate"])
        # Join DataFrame and remove duplicates
        global players_teams
        players_teams = pd.concat([players_teams, team_relations_data], ignore_index=True).drop_duplicates(
            subset=["fullName", "birthDate", "teamId"])


    print(f"{teamName} data correctly exported.")


if __name__ == '__main__':

    # Start data extraction by passing League URL and name.
    extract_teams("https://www.bdfutbol.com/en/t/tita2023-24.html", "Serie A")
    extract_teams("https://www.bdfutbol.com/en/t/teng2023-24.html", "Premier League")
    extract_teams("https://www.bdfutbol.com/en/t/t2023-24.html", "La Liga")
    extract_teams("https://www.bdfutbol.com/en/t/tfra2023-24.html", "Ligue 1")
    extract_teams("https://www.bdfutbol.com/en/t/tger2023-24.html", "Bundesliga")

    # Export updated DataFrame in 'players.xlsx'
    players.to_excel('players.xlsx', index=False)

    # Export updated DataFrame in 'players_teams.xlsx'
    players_teams.to_excel('players_teams.xlsx', index=False)

    print(f"Extraction completed")
