# Soccer-Players-Database

This Python script let you scrape soccer players and teams data from a [public website](https://www.bdfutbol.com/en/index.html).

### 🏟️ Supported leagues
* Serie A (Italy)
* Premier League (England)
* LaLiga (Spain)
* Bundesliga (Germany)
* Ligue 1 (France)

## Features

The script creates three .xlsx/.csv files:

* players.xlsx
 
| displayName | fullName | nation | **birthDate** | link |
|-------------|----------|--------|---------------|------|
* teams.xlsx
 
| teamId | teamName | leagueName |
|--------|----------|------------|
* players_teams.xlsx
 
| fullName | birthDate | teamId | 
|----------|-----------|--------|

We have imported `threading` package to handle parallel execution: teams in a league are processed simultaneously. 
Data are temporarily stored in global variables thanks to Thread locks.

## Contribute

Contributions are always welcome! Please create a PR.
## :pencil: License

This project is licensed under [MIT](https://opensource.org/licenses/MIT) license.
