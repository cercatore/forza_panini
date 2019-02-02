from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import urllib2

CURRENT_YEAR = 17
N_SEASON_HISTORY = 5
#https://cloud.google.com/python/setup

class PlayerProfile:
	def __init__(self, playerUrl, pageScraper):
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36')]
		soup = pageScraper( opener.open(playerUrl), 'html.parser' )
		playerAttributes = {}

		#scraping profile page information
		playerAttributes["name"] = soup.find("div", class_="dataMain").find("h1").text
		playerAttributes["img"] = soup.find("div", class_="dataBild").find('img').attrs["src"]
		StoredAttributes = ["Age:", "Height:", "Nationality:", "Position:", "Foot:", "Current club:"]
		for entry in soup.find("table", class_="auflistung").find_all("th"):
			key = entry.text.strip()
			val = entry.find_next_sibling().text
			if key in StoredAttributes:
				playerAttributes[ key[:-1].lower()] = val.strip()
		#cleaning some entries
		if "height" in playerAttributes:
			#converting height in meters str to cm int
			meter, centimeters = re.search("(\d),(\d+)",playerAttributes["height"]).groups()
			playerAttributes["height"] = int(meter)*100 + int(centimeters)
		if "position" in playerAttributes:
			playerAttributes["position"] = "CF" if "Centre-Forward" in playerAttributes["position"] else "W"
		if "age" in playerAttributes:
			playerAttributes["age"] = int( playerAttributes["age"])

		self.PlayerData = pd.Series(playerAttributes)
		print( "\t%s done" %self.PlayerData["name"])
		#scraping performance page information
	def performance(self):
		urlPerf = playerUrl.replace("profil","leistungsdatendetails")
		soup = bs
		performanceColumns = ("season", "games", "goals", "assists", "minutes")
		performanceRows = pd.DataFrame( {col:[] for col in performanceColumns})
		for row in soup.find("div", class_="responsive-table").find("tbody").find_all("tr"):
			#try:
			rowContents = PlayerProfile.readRow( row)
			#except:
			#	 print( row)
			#else:
			#	 pass
			year = rowContents[0]
			if re.match( "\d{4}", year):
				year = int( year[2:])
				year = "%02d/%02d" %(year-1, year)
				rowContents[0] = year
			if not re.match( "\d{2}\/\d{2}", year):
				raise ValueError("Wrong format for played year")
			if int( year[:2]) < CURRENT_YEAR - N_SEASON_HISTORY:
				break
			#print( rowContents)
			performanceRows = performanceRows.append( {col:val for col, val in zip(performanceColumns, rowContents)}, ignore_index=True)
		performanceDF = performanceRows.groupby("season").sum()
		#converting to serie
		performanceSeries = pd.Series( {"%s %s" %(row, col): performanceDF[col][row] for row in performanceDF.index for col in performanceDF.columns})

		self.PlayerData = pd.Series( playerAttributes).append( performanceSeries)
		print( "\t%s done" %self.PlayerData["name"])

	def __str__(self):
		return "Performance profile for %s" % self.PlayerData["name"]

	def __repr__(self):
		return "< profile of %s >" % self.PlayerData["name"]

	@staticmethod
	def readRow( row):
		cells = row.find_all( "td")
		cells = list( map( lambda x : x.text.strip(), cells))
		year = cells[0]
		games_played = cells[4]
		goals_scored = cells[6]
		assists = cells[7]
		minutes_played = cells[-1]
		games_played = int(games_played) if games_played != "-" else 0
		goals_scored = int(goals_scored) if goals_scored != "-" else 0
		assists = int(assists) if assists != "-" else 0
		minutes_played = int( minutes_played[:-1].replace(".","")) if minutes_played != "-" else 0
		return [year, games_played, goals_scored, assists, minutes_played]

if __name__ == '__main__':
	url = 'https://www.transfermarkt.it/isaac-drogba/profil/spieler/568147'
	player = PlayerProfile(url, bs)
	print player.PlayerData
