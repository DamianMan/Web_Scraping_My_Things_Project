from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import re





app = Flask(__name__)



@app.route("/")
def home():

    return render_template("index.html")

@app.route("/nba")
def nba():
    request = requests.get('https://www.nba.com/stats')
    html_text = request.text
    soup = BeautifulSoup(html_text, 'html.parser')
    #SOUP PER POINTS
    players = soup.find_all(name='tr', class_='LeaderBoardPlayerCard_lbpcTableRow___Lod5')[:5]
    players = [player.get_text() for player in players]

    # SOUP PER REBOUNDS
    rebounds = soup.find_all(name='tr', class_='LeaderBoardPlayerCard_lbpcTableRow___Lod5')[5:10]
    rebounds = [reb.get_text() for reb in rebounds]

    # SOUP PRE THREE POINT MADE
    three_points = soup.find_all(name='tr', class_='LeaderBoardPlayerCard_lbpcTableRow___Lod5')[30:35]
    three_points = [three.get_text() for three in three_points]

    #CLEANING PLAYER POINTS DATA
    points = [player[-2:] for player in players]
    players = [player[:-2] for player in players]
    dict_points = dict(zip(players,points))

    #CLEANING PLAYER REBOUNDS DATA
    rebound_points = [reb[-2:] for reb in rebounds]
    player_rebounds = [reb[:-2] for reb in rebounds]
    dict_rebounds = dict(zip(player_rebounds,rebound_points))

    #CLEANING PLAYER PER THREE POINTS MADE
    real_three_points = [three[-1:] for three in three_points]
    players_three_points = [three[:-1] for three in three_points]
    dict_three_points = dict(zip(players_three_points,real_three_points))

    # CREATING CSV FILE FROM DATA SCRAPE
    data = []
    for points in dict_points:
        data_ap = {'Player':points[2:],
            'Points': dict_points[points],}
        data.append(data_ap)

    for rebound in dict_rebounds:
        data_ap = {'Player': rebound[2:],
                   'Rebounds': dict_rebounds[rebound], }
        data.append(data_ap)

    for three in dict_three_points:
        data_ap = {'Player': three[2:],
                   'Rebounds': dict_three_points[three], }
        data.append(data_ap)

    df = pd.DataFrame(data, columns=['Player','Points','Rebounds', 'Three Points'])
    print(df['Player'])
    df.to_csv('nba_stats.csv')


    return render_template('nba.html', points=dict_points, rebounds=dict_rebounds,
                           three_points=dict_three_points)

@app.route("/padel")
def padel():
    request = requests.get('https://worldpadeltour.com/jugadores')
    html_page = request.text
    soup = BeautifulSoup(html_page, 'html.parser')
    players = soup.find_all(name='p', class_='name')
    players = [player.get_text() for player in players][20:30]

    all = soup.select('p')
    all = [p.get_text() for p in all]

    rank_row = [p for p in all][91:]
    n = 0
    rank = []
    pos = [2,5,8,11,14,17,20,23,26,29]
    for p in range(len(rank_row)):
        if n in pos:
            rank.append(rank_row[n])
        n += 1

    points = []
    points_raw = [all[p] for p in range(len(all))][92:]
    for p in range(len(points_raw)):
        if p in pos:
            points.append(points_raw[p])


    with open('padel.csv', 'w', newline='') as padel_file:
        columns = ['Rank', 'Player', 'Points']
        writer = csv.DictWriter(padel_file, fieldnames=columns)
        for n in range(len(rank)):
            writer.writerow({'Rank': rank[n], 'Player': players[n], 'Points': points[n]})




    return render_template("padel.html", rank=rank, players=players, points=points)

@app.route("/video-games")
def video_games():
    request = requests.get('https://www.githyp.com')
    html_page = request.text
    soup = BeautifulSoup(html_page, 'html.parser')

    games_title = soup.find_all(name='h2', class_='item-title')
    games_title = [re.sub(r"[\n\t\s]*", "", game.get_text()) for game in games_title][:10]

    num_players = soup.find_all(name='span', class_='comments-link')
    num_players = [re.sub(r"[\n\t\s]*", "", num.get_text())[:-7] for num in num_players][:10]
    print(num_players)

    dict_video_games = dict(zip(games_title, num_players))

    with open('video-game.csv', 'w', newline='') as game_file:
        columns = ['Video Game Title', 'Players']
        writer = csv.DictWriter(game_file, fieldnames=columns)
        for game in dict_video_games:
            writer.writerow({'Video Game Title':game, 'Players':dict_video_games[game]})

    return render_template("video_games.html", video_games=dict_video_games)




if '__main__' == __name__:
    app.run(debug=True)