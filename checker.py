import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
from scheduleUpdater import return_first_game, get_next_gametime, update_schedule

TOKEN = "TOKEN"
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has logged on')
    global seconds_until_game
    seconds_until_game = get_seconds(get_next_gametime("ducksScheduleUpdated.json"))
    countdown_to_next_game.start()
    

@bot.command(name="nextGame")
async def nextGame(ctx):
    game = return_first_game("ducksScheduleUpdated.json")
    date = game['dateET']
    time = int(date[11:13])-3
    await ctx.send(f'the next eligible game is an NHL game. '
                   f'the Anaheim Ducks are playing agianst the {game["awayEventResult"]["competitor"]["name"]}'
                   f' on {date[5:10]}-{date[0:4]} at {time}{date[13:]}PT')

def get_seconds(game_time):
    # Convert the date string to a datetime object
    
    target_date = datetime.strptime(game_time, "%Y-%m-%d %H:%M:%S")

    # Set the time zone to Eastern Time
    et_timezone = pytz.timezone('US/Eastern')

    # Get the current time in Eastern Time (aware of the timezone)
    current_time_et = datetime.now(et_timezone)
    target_date = et_timezone.localize(target_date)

    # Calculate the time difference
    time_difference = target_date-current_time_et

    return [int(time_difference.total_seconds())]
        
@tasks.loop(seconds=60)
async def countdown_to_next_game():
    global seconds_until_game
    print(seconds_until_game[0])
    if seconds_until_game[0] <= 0:


        channel_id = 1187128458774585396
        channel = bot.get_channel(channel_id)

        if channel:
            await channel.send(f'the game has started! support your local team and potentially win free chicken!')

        # call a new task function that calls the data from the live data and checks for goals scored

        #update the json file
        update_schedule("ducksScheduleUpdated.json")

        seconds_until_game = get_seconds(get_next_gametime("ducksScheduleUpdated.json"))

    else:
        seconds_until_game[0] -= 60
    



bot.run(TOKEN)