from flask import Flask, render_template
import requests
import json
import locale
import config
from babel.numbers import format_currency

app = Flask(__name__)

# GET DATA FROM THE API
#Headers to retrieve data from biwenger
headers={
    'Authorization': config.authorization,
    'X-League': config.x_league,
    'X-User': config.x_user,
    'Accept': 'application/json'
    }

#Get Market database
url='https://biwenger.as.com/api/v2/league/' + config.x_league + '/board?type=transfer,market,exchange,loan,loanReturn,clauseIncrement&offset=0&limit=500'
response = requests.get(url,headers=headers)
marketDatabase = json.loads(response.text)

#Get Vodka Juniors database
url = 'https://biwenger.as.com/api/v2/league?include=all,-lastAccess&fields=*,standings,group,settings(description)'
response = requests.get(url,headers=headers)
leagueDatabase = json.loads(response.text)

#Get all players database
url = 'https://cf.biwenger.com/api/v2/competitions/la-liga/data?lang=es&score=5'
response = requests.get(url)
playersDatabase = json.loads(response.text)

#Get all the teams on the league
teamsDatabase = []
for teams in leagueDatabase['data']['standings']:
    teamsDatabase.append(teams['name'])

#Define structures
operation = {
    "from":"",
    "to":"",
    "playerid":"",
    "playername":"",
    "amount":""
    }
player = {
    "name":"",
    "position":"",
    "points":"",
    "games":"",
    "price":""
    }

marketMovements = []
teamPlayers = []

teamFormation = {
    "teamName":"",
    "players":""
}
leagueFormations = []

#Write the data from the market
for gamers in marketDatabase['data']:
    if gamers['type'] == 'transfer':
        for transaction in gamers['content']:
            if 'type' in transaction:
                if transaction['type'] == 'clause':                   
                    operation["from"] = transaction['from']['name']
                    operation["to"] = transaction['to']['name']
                    operation["playerid"] = transaction['player']
                    if str(transaction['player']) in playersDatabase['data']['players']:
                        operation["playername"] = playersDatabase['data']['players'][str(transaction['player'])]['name']
                    else:
                        operation["playername"] = str(transaction['player'])

                    operation["amount"] = format_currency(transaction['amount'] , 'EUR', locale='de_DE',decimal_quantization=False)

                    marketMovements.append(operation.copy())
            else:
                if 'bids' in transaction:
                    operation["from"] = "Market"
                    operation["to"] = transaction['to']['name']
                    operation["playerid"] = transaction['player']
                    if str(transaction['player']) in playersDatabase['data']['players']:
                        operation["playername"] = playersDatabase['data']['players'][str(transaction['player'])]['name']
                    else:
                        operation["playername"] = str(transaction['player'])

                    operation["amount"] = format_currency(transaction['amount'] , 'EUR', locale='de_DE')

                    marketMovements.append(operation.copy())


                elif 'from' in transaction:
                    operation["from"] = transaction['from']['name']

                    if 'to' in transaction:
                        if 'name' in transaction['to']:
                            operation["to"] = transaction['to']['name']
                        else:
                            operation["to"] = transaction['to']
                    else:
                        operation["to"] = "Market"

                    operation["playerid"] = transaction['player']
                    if str(transaction['player']) in playersDatabase['data']['players']:
                        operation["playername"] = playersDatabase['data']['players'][str(transaction['player'])]['name']
                    else:
                        operation["playername"] = str(transaction['player'])

                    operation["amount"] = format_currency(transaction['amount'] , 'EUR', locale='de_DE')

                    marketMovements.append(operation.copy())

    elif gamers['type'] == 'market':
        for transaction in gamers['content']:
            if 'type' in transaction:
                if transaction['type'] == 'clause':
                    operation["from"] = transaction['from']['name']
                    operation["to"] = transaction['to']['name']
                    operation["playerid"] = transaction['player']
                    if str(transaction['player']) in playersDatabase['data']['players']:
                        operation["playername"] = playersDatabase['data']['players'][str(transaction['player'])]['name']
                    else:
                        operation["playername"] = str(transaction['player'])

                    operation["amount"] = format_currency(transaction['amount'] , 'EUR', locale='de_DE')

                    marketMovements.append(operation.copy())

            else:
                if 'bids' in transaction:
                    operation["from"] = "Market"
                    operation["to"] = transaction['to']['name']
                    operation["playerid"] = transaction['player']
                    if str(transaction['player']) in playersDatabase['data']['players']:
                        operation["playername"] = playersDatabase['data']['players'][str(transaction['player'])]['name']
                    else:
                        operation["playername"] = str(transaction['player'])

                    operation["amount"] = format_currency(transaction['amount'] , 'EUR', locale='de_DE')

                    marketMovements.append(operation.copy())

                else:
                    operation["from"] = "Market"

                    if 'to' in transaction:
                        if 'name' in transaction['to']:
                            operation["to"] = transaction['to']['name']
                        else:
                            operation["to"] = transaction['to']
                    else:
                        operation["to"] = "Market"

                    operation["playerid"] = transaction['player']
                    if str(transaction['player']) in playersDatabase['data']['players']:
                        operation["playername"] = playersDatabase['data']['players'][str(transaction['player'])]['name']
                    else:
                        operation["playername"] = str(transaction['player'])

                    operation["amount"] = format_currency(transaction['amount'] , 'EUR', locale='de_DE')

                    marketMovements.append(operation.copy())


#Write the data from the formations
for selectedTeamName in teamsDatabase:
    teamCode= 0
    for teams in leagueDatabase['data']['standings']:
        if teams['name'] == selectedTeamName:
            teamCode = teams['id']

    url = 'https://biwenger.as.com/api/v2/user/' + str(teamCode) + '?fields=*,account(id),players(id,owner),lineups(round,points,count,position),league(id,name,competition,mode,scoreID),seasons,offers,lastPositions'

    #Get the team database with the code
    response = requests.get(url,headers=headers)
    teamDatabase = json.loads(response.text)

    #Get the players
    for players in teamDatabase['data']['players']:
        if str(players['id']) in playersDatabase['data']['players']:
            #Write Name
            player['name'] = playersDatabase['data']['players'][str(players['id'])]['name']
            #Write Position
            positionString = playersDatabase['data']['players'][str(players['id'])]['position']
            if positionString == 1:
                player['position'] = "Portero"
            elif positionString == 2:
                player['position'] = "Defensa"
            elif positionString == 3:
                player['position'] = "Mediocentro"
            elif positionString == 4:
                player['position'] = "Delantero"
            #Write Points
            player['points'] = playersDatabase['data']['players'][str(players['id'])]['points']
            #Write Games
            player['games'] = playersDatabase['data']['players'][str(players['id'])]['playedAway'] + playersDatabase['data']['players'][str(players['id'])]['playedHome']
            #Write Price
            player['price'] = format_currency(int(playersDatabase['data']['players'][str(players['id'])]['price']), 'EUR', locale='de_DE')
            #Write Price Increment
            #ws.cell(i,16).value = playersDatabase['data']['players'][str(players['id'])]['priceIncrement']
        teamPlayers.append(player.copy())

    teamFormation['teamName'] = (selectedTeamName)
    teamFormation['players'] = (teamPlayers.copy())
    teamPlayers.clear()

    leagueFormations.append(teamFormation.copy())




@app.route("/")
def index():
    return render_template(
    'index.html', teamsDatabase=teamsDatabase)

@app.route("/hello/<string:name>/")
def hello(name):
    return render_template(
    'test.html',name=name, )

@app.route("/team/<string:name>/")
def team(name):
    return render_template(
    'test2.html',name=name, marketMovements=marketMovements, teamDatabase=teamsDatabase, leagueFormations=leagueFormations, teamsDatabase=teamsDatabase)

@app.route("/members")
def members():
    return "Members"

@app.route("/members/<string:name>/")
def getMember(name):
    return name

if __name__ == "__main__":
    app.run()