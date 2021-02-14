#All needed libraries
import discord
from discord.ext import commands
import time
import asyncio
import random
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


#Sets up the directory
os.chdir("Your dir to this file")

#Soup setup
URL = 'https://www.worldometers.info/coronavirus/country/us/'
headers = {"User-Agent":'Your User Agent'}
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')




#Discord.py setup
client = discord.Client()
bot = commands.Bot(command_prefix = '.')

#Events
@bot.event
async def on_ready():
    #When the bot is ready, it will print in Command Prompt
    await bot.change_presence(activity=discord.Game("Custom activity here"))
    print("Bot is ready")

#Commands
@bot.command()
async def ping(ctx):
    #responds with the ping
    await ctx.send(f'Pong! :ping_pong: {round(bot.latency * 1000)}ms')

@bot.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ['Yes', 'Maybe', 'No', 'Ask later']
    #Makes a random choice from the above list and retuns it
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@bot.command()
async def rps(ctx, *, choice):

    #The CPU makes a choice
    options = ['rock', 'paper', 'scissors']
    cpuchoice = random.choice(options)
    choice = choice.lower()
    
    if choice not in options:
        await ctx.send(f'Please use only Rock, Paper, or Scissors.')
    
    #Determines the outcome of the game
    if cpuchoice == choice:
        await ctx.send(f'We both chose {cpuchoice}')
        await add_tie(ctx)

    if cpuchoice == 'rock' and choice == 'scissors':
        await ctx.send(f'You chose: :v:\nI chose: :fist:\nYou lose')
        await add_loss(ctx)

    if cpuchoice == "scissors" and choice == 'rock':
        await ctx.send(f'You chose: :fist:\nI chose: :v:\nYou win')
        await add_win(ctx)

    if cpuchoice == 'paper' and choice == 'rock':
        await ctx.send(f'You chose: :fist:\nI chose: :raised_hand:\nYou lose')
        await add_loss(ctx)

    if cpuchoice == "rock" and choice == 'paper':
        await ctx.send(f'You chose: :raised_hand:\nI chose: :fist:\nYou win')
        await add_win(ctx)

    if cpuchoice == 'scissors' and choice == 'paper':
        await ctx.send(f'You chose: :raised_hand:\nI chose: :v:\nYou lose')
        await add_loss(ctx)

    if cpuchoice == "paper" and choice == 'scissors':
        await ctx.send(f'You chose: :v:\nI chose: :raised_hand:\nYou win')
        await add_win(ctx)

@bot.command()
async def cases(ctx):

    #Uses BeautifulSoup to grab data off of worldometers and displays it.
    uscases = soup.find('div', class_='maincounter-number').get_text()

    await ctx.send(f':flag_us: cases: {uscases}')

@bot.command()
async def exit(ctx):
    #in case you need to exit the program
    quit()

@bot.command()
async def score(ctx):
    #Checks to see if that user has an account
    await open_account(ctx.author)
    user = ctx.author
    users = await get_score_data()

    #Gets the data from score.json
    num_of_wins = users[str(user.id)]["Wins"]
    num_of_lose = users[str(user.id)]["Losses"]
    num_of_ties = users[str(user.id)]["Ties"]
    num_of_correct = users[str(user.id)]["Correct Answers"]

    #Checks to see if we are dividing by zero
    if num_of_lose == 0:
        average = 0
        taverage = 0
    else:
        average = num_of_wins / num_of_lose
        taverage = truncate(average, 2)

    #Sends an embed with the data
    em = discord.Embed(title = f"{ctx.author.name}'s score card")
    em.add_field(name = "Wins :trophy::", value = num_of_wins)
    em.add_field(name = "Losses :x::", value = num_of_lose)
    em.add_field(name = "Ties :necktie::", value = num_of_ties)
    em.add_field(name = "W/L Ratio: ", value = taverage)
    em.add_field(name = "Correct Answers: ", value = num_of_correct)
    await ctx.send(embed = em)

@bot.command()
async def isit(ctx):
    now = datetime.now().time()
    if now.hour == 4 and now.minute == 20:
        await ctx.send(":white_check_mark:")
    else:
        await ctx.send(':x:')

@bot.command()
async def trivia(ctx):
    #Chooses a random question number
    x = random.randrange(15)
    y = str(x)

    #Opens questions.json
    with open('questions.json') as f:
        ques = json.load(f)

    #Makes an embed with the question and the answers
    em = discord.Embed(title = ques['questions']['numbers'][y]['question'])
    em.add_field(name = "A.", value = ques['questions']['numbers'][y]['a'])
    em.add_field(name = "B.", value = ques['questions']['numbers'][y]['b'])
    msg = await ctx.send(embed = em)
    await ctx.send('React with 🅰️ or 🅱️ to answer')

    #If a question is reacted with the correct letter, it responds with correct and adds a point to their score card
    if (x%2) == 0:
        reaction, user = await bot.wait_for('reaction_add', check=lambda reaction, user: reaction.emoji == '🅱️')
        await ctx.send("Correct")
        await add_correct(ctx)
    else:
        reaction, user = await bot.wait_for('reaction_add', check=lambda reaction, user: reaction.emoji == '🅰️')
        await ctx.send("Correct")
        await add_correct(ctx)

@bot.command()
async def meme(ctx):

    num = random.randint(0,"Number of memes")
    #Take that number and tries to see if an image file is named that

    try:
        await ctx.send(file=discord.File(f'{num}.jpg'))
    except:
        await ctx.send(file=discord.File(f'{num}.png'))


#Functions
async def open_account(user):
    users = await get_score_data()
    #checks to see if that user has played a game before and if not makes them an account
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["Wins"] = 0
        users[str(user.id)]["Losses"] = 0
        users[str(user.id)]["Ties"] = 0
        users[str(user.id)]["Correct Answers"] = 0

    with open("score.json", 'w') as f:
        json.dump(users,f)
    return True

async def get_score_data():
    #opens up the score.json file and returns the users
    with open("score.json", 'r') as f:
        users = json.load(f)
    return users

async def add_correct(ctx):
    await open_account(ctx.author)
    users = await get_score_data()
    user = ctx.author
    #Adds a point to the correct answers section of the score card
    num_of_correct = users[str(user.id)]["Correct Answers"] = num_of_correct = users[str(user.id)]["Correct Answers"] + 1
    with open("score.json", 'w') as f:
        json.dump(users,f)

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

async def add_loss(ctx):
    await open_account(ctx.author)

    users = await get_score_data()
    user = ctx.author
    num_of_lose = users[str(user.id)]["Losses"] = num_of_lose = users[str(user.id)]["Losses"] + 1
    with open("score.json", 'w') as f:
        json.dump(users,f)
    return True

async def add_win(ctx):
    await open_account(ctx.author)

    users = await get_score_data()
    user = ctx.author
    num_of_wins = users[str(user.id)]["Wins"] = users[str(user.id)]["Wins"] + 1
    with open("score.json", 'w') as f:
        json.dump(users,f)
    return True

async def add_tie(ctx):
    await open_account(ctx.author)

    users = await get_score_data()
    user = ctx.author
    num_of_ties = users[str(user.id)]["Ties"] = num_of_ties = users[str(user.id)]["Ties"] + 1
    with open("score.json", 'w') as f:
        json.dump(users,f)
    return True



bot.run("Your key")
