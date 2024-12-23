import sqlite3
import pandas as pd
import matplotlib.dates as mdates 
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.patches as mpatches

print("Updating VADER...")
nltk.download('vader_lexicon')

#query data
def queryData(connection, date):
    cursor = connection.execute("SELECT mood, notes FROM data where date = ?", (date,))
    row = cursor.fetchone()
    if row:
        column_names = [description[0] for description in cursor.description]
        return dict(zip(column_names, row))
    else:
        return None
    
#insert new data into db
def insertNewData(connection, date, day, mood, notes=""):
    cursor = connection.execute("SELECT date FROM data where date = ?", (date,))
    result = cursor.fetchone()
    
    if result: #if already present, update. else insert new data data
        mytuple = (mood, notes, date)
        try:
            connection.execute(f"UPDATE data SET mood = ?, notes = ? WHERE date = ?", (mytuple))
            connection.commit()
            print("Updated successfully...")
            return True
        except sqlite3.IntegrityError as e:
            print(f"ERROR: {e}")
            return False
    else:
        try:
            mytuple = (date, day, mood, notes)
            connection.execute("INSERT INTO data VALUES (?, ?, ?, ?)", mytuple)
            connection.commit()
            print("Updated successfully...")
            return True
        except sqlite3.IntegrityError as e:
            print(f"ERROR: {e}")
            return False

#delete data from db
def deleteSelectedData(connection, date):
    try:
        connection.execute("DELETE FROM data WHERE date = ?", (date,))
        connection.commit()
        print("Deleted successfully...")
        return True
    except sqlite3.IntegrityError as e:
        print(f"ERROR: {e}")
        return False

#machine learning to pickup language from notes for sentiment anlaysis
def mlAnalysis(df):
    def ml_logic(note):
        if note != "":
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(note)

            if scores['compound'] >= 0.05:
                return 'Positive'
            elif scores['compound'] <= -0.05:
                return 'Negative'
            else:
                return 'Neutral'
        else:
            return 'NULL'
    
    df['sentiment'] = df['notes'].apply(ml_logic)

#visualize data from db as line graph
def visualAnalysis(connection):
    #create df from data
    df = pd.read_sql_query("SELECT * FROM data;", connection)

    if df.empty:
        return False

    #sort it in increasing order for date/time
    df['date'] = pd.to_datetime(df['date'])  
    df.sort_values(by='date', inplace=True)

    #apply sentiment analysis to notes if any
    mlAnalysis(df)

    #generate graph based off of it
    colours = {
        "Positive" : "green",
        "Negative" : "red",
        "Neutral" : "yellow",
        "NULL" : "black"
    }
    df['colour'] = df['sentiment'].map(colours)#colour

    plt.plot(df['date'], df['mood'], linestyle='-', color='black', label='Trend Line', zorder=1)
    plt.scatter(df['date'], df['mood'], c=df['colour'], label='Mood', edgecolor='black', s=50, zorder=2)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(FixedLocator(df['date'].map(mdates.date2num).unique()))
    ax.set_yticks(range(1, 11))

    positive_dot = mpatches.Patch(color='green', label='Positive') 
    negative_dot = mpatches.Patch(color='red', label='Negative') 
    neutral_dot = mpatches.Patch(color='yellow', label='Neutral') 
    null_dot = mpatches.Patch(color='black', label='No Entry') 

    plt.legend(handles=[positive_dot, negative_dot, neutral_dot, null_dot], title='Notes Analysis', loc='best')
    plt.xlabel('Date')
    plt.ylabel('Mood')
    plt.title('Mood Trend')
    plt.xticks(rotation=45)  
    plt.tight_layout()
    plt.show()
