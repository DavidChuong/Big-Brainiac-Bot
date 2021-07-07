import os
import discord
import requests
import json
from keepalive import keep_alive
import random
from replit import db

#Setup to grab member info as soon as they join.
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

my_access = os.environ['ACCESS'] #Obtain access key for API.

#Function that accesses information about a superhero from the SuperHero API and returns a dictionary containing all of the information.
def get_info(id):
  """Return information about a superhero in the form of a dictionary given the ID of the superhero."""
  #Obtain URL for the superhero we are trying to access information about.
  url = "https://superheroapi.com/api/" + str(my_access) + "/" + str(id)
  #Request json of info and load it onto a dictionary.
  info_json = requests.get(url) 
  info_dict = json.loads(info_json.text) 
  return info_dict

#Function that parses a dictionary into a sendable message on Discord.
def format_info(info, author):
  """Return a string message that neatly formats the information contained about a superhero or villain within a dictionary."""
  formatted_info = "" #Initialize giant string we will use to display all of our info.
  #Notify user of which superhero/villain's info was requested.
  formatted_info += ("Here is the information you requested about " + info["name"] + ", " + author + ".\n\n")
  #Go through each category-subinformation pair in the dictionary.
  for info_type, subinfo in info.items():
    #Skip the pairs where the categories are response, id, or name.
    if (info_type != "response" and info_type != "id" and info_type != "name"):
      #State which category of information we are going to display (in boldface).
      formatted_info += "**" + info_type.upper() + "**\n"
      #Go through each each data entry in each category.
      for subinfo_type, data in subinfo.items():
        #If the data entry is a URL, just display the URL.
        if (subinfo_type == "url"):
          formatted_info += data
        #Otherwise, display the data along with what type of data it is.
        else:
          data_type = subinfo_type.replace("-", " ").title()
          if (isinstance(data, list)):
            formatted_info += data_type + ": " + data[0]
            for item in data[1:]:
              formatted_info += ", " + item 
            formatted_info += "\n"
          else:
            formatted_info += data_type + ": " + data + "\n"
      formatted_info += "\n"
  return formatted_info

#Function that searches for a character's possible IDs in the API.
def search_API(name):
  """Return a list of possible IDs that correlate to the name of a superhero or villain."""
  #Obtain URL for searching the character's name.
  url = "https://superheroapi.com/api/" + str(my_access) + "/search/" + name
  #Request json of info and load it onto a dictionary.
  search_json = requests.get(url)
  search_dict = json.loads(search_json.text)
  #Find the list of search results in the dictionary.
  if (search_dict["response"] == "success"):
    results_list = search_dict["results"]
  else:
    results_list = []
  #Initialize list of possible IDs to an empty list.
  possible_IDs = []
  #Look through each search result and obtain the ID correlating to that character, then add it to our list of possible IDs.
  for search_result in results_list:
    possible_IDs.append(search_result["id"])
  return possible_IDs

#Function that neatly formats the results of a search.
def format_results(possible_IDs, search_term):
  """Return a neatly formatted string that gives the list of possible IDs correlating to a search term."""
  #Initialize the return string.
  results = "Here are the possible IDs that match the search term \"" + search_term + "\": "
  #If there are no matching IDs, say that none were found.
  if (len(possible_IDs) == 0):
    results += "None found.\n\n"
    results += "It appears as if no matching ID for this character was found in my database. It is possible that they are not a threat for a truly intelligent specimen such as myself. Perhaps you will have more luck searching through a measly human database.\n\n"
    results += "https://www.google.com/search?q=" + search_term
  #Otherwise, list all possible IDs matching the search term we used.
  else:
    results += possible_IDs[0]
    for id_num in possible_IDs[1:]:
      results += ", " + id_num
  return results

#Function that predicts the outcome of a battle.
def predict_outcome(ids):
  """Return a string message that predicts the outcome of a battle between two characters."""
  #Obtain dictionaries of the characters.
  info_1 = get_info(ids[0])
  info_2 = get_info(ids[1])
  #Obtain the names of the characters.
  name_1 = info_1["name"]
  name_2 = info_2["name"]
  #Obtain powerstats for both characters.
  stats_1 = info_1["powerstats"]
  stats_2 = info_2["powerstats"]
  #Extract stats from the dictionaries and sum them up.
  score_1 = 0;
  score_2 = 0;
  for stat in stats_1.values():
    score_1 += int(stat)
  for stat in stats_2.values():
    score_2 += int(stat)
  #Initialize message that will be sent.
  result = "*Neural network is now simulating battle between " + name_1 + " and " + name_2 + ".*\n\n"
  #Determine the probability of each character winning the battle.
  total_score = score_1 + score_2
  calc_1 = (score_1/total_score) * 100
  calc_2 = (score_2/total_score) * 100
  prob_1 = str(round(calc_1, 2)) + "%"
  prob_2 = str(round(calc_2, 2)) + "%"
  #Display this result to the user. Bolded result indicates which character has a higher chance of winning.
  if (score_1 > score_2):
    name_1 = "**" + name_1 + "**"
    prob_1 = "**" + prob_1 + "**" 
  elif (score_2 > score_1):
    name_2 = "**" + name_2 + "**"
    prob_2 = "**" + prob_2 + "**"
  result += "According to my calculations, " + name_1 + " has a " + prob_1 + " chance of winning the battle, while " + name_2 + " has a " + prob_2 + " chance of winning the battle."
  return result

#Function that generates a random IQ assessment of a user.
def rate_iq(author):
  """Return random IQ assessment."""
  #Initialize message and IQ that will be sent.
  rating = "According to my calculations, your IQ is "
  iq = 0
  #If the user does not have an IQ rating, generate a random IQ rating that is between 1 and 200 (inclusive) and store it in the database.
  if author.name not in db.keys():
    db[author.name] = {}
    iq = random.randrange(1, 201)
    db[author.name]["IQ"] = iq
  elif "IQ" not in db[author.name].keys():
    iq = random.randrange(1, 201)
    db[author.name]["IQ"] = iq
  #Otherwise, pull their IQ rating from the database.
  else:
    iq = db[author.name]["IQ"]
  #Notify the user of what their IQ is.
  rating += "**" + str(iq) + "**, " + author.mention + ". This means that you "
  #Based on the random IQ that was generated, assess the user's intelligence.
  if (iq < 25):
    rating += "have a profound mental disability. Idiot!"
  elif (iq < 40):
    rating += "have a severe mental disability. Idiot!"
  elif (iq < 55):
    rating += "have a moderate mental disability. Idiot!"
  elif (iq < 70):
    rating += "have a mild mental disability. Idiot!"
  elif (iq < 85):
    rating += "have a borderline mental disability. Idiot!"
  elif (iq < 115):
    rating += "have average intelligence. Typical puny brained human!"
  elif (iq < 130):
    rating += "are above average. But only for a puny brained human!"
  elif (iq < 145):
    rating += "are moderately gifted. But not gifted enough, puny brained human!"
  elif (iq < 160):
    rating += "are highly gifted. But only for a puny brained human!"
  elif (iq < 180):
    rating += "are exceptionally gifted. But only for a puny brained human!"
  else:
    rating += "are profoundly gifted. Impressive, human. Perhaps you will be a worthly rival for the Great Brainiac."
  return rating

#Function that absorbs information that a user posts.
def absorb_info(info, user, info_type):
  """Absorbs a URL into Brainiac's database."""
  #Add URL to list of links that have been posted.
  if user in db.keys():
    if info_type in db[user].keys():
      stored_info = db[user][info_type]
      stored_info.append(info)
      db[user][info_type] = stored_info
    else:
      db[user][info_type] = [info]
  #Otherwise, create a new list for the user.
  else:
    db[user] = {}
    db[user][info_type] = [info]

#Notifies operator when bot is logged onto the server.
@client.event
async def on_ready():
  await client.change_presence(activity = discord.Game('?help'))
  print('We have logged in as: {0.user}'.format(client))

#Sends welcome message to a person when they first join the server.
@client.event
async def on_member_join(member):
  guild = client.get_guild(849063884992151552)
  channel = guild.get_channel(849063885519585302)
  welcome = "Welcome, " + member.mention + ". I look forward to adding your knowledge to my database."
  await channel.send(welcome)

#Perform an action based on the message a user sends.
@client.event
async def on_message(message):
  #Displays the help menu.
  if (message.content.startswith('?help')):
    help_message = "Greetings, intellectually inferior specimen. Below is a list of commands you may use to access my vast archive of acquired knowledge.\n\n"
    commands = ['**GENERAL COMMANDS**',
                '?help - Displays the help menu.', 
                '?bio - Provides more information about Brainiac\'s mission.\n',
                '**SUPERHERO DATABASE COMMANDS**',
                '?info <id> - Displays detailed information about any superhero or supervillain given an ID number.',
                '\tEx: ?info 231',
                '?search <name> - Gives a list of IDs that possibly match the name of a superhero or supervillain.',
                '\tEx: ?search batman',
                '?battle <id 1> <id 2> - Simulates a virtual battle between two super characters and predicts the estimated outcome.',
                '\tEx: ?battle 66 140\n',
                '**USER DATABASE COMMANDS**',
                '?me - Displays all information that Brainiac has gathered about you.',
                '?iq - Assesses your IQ.',
                '?links - Retrieves a list of all of the links you have posted that Brainiac has absorbed into his database.',
                '?quotes - Retrieves a list of all of the quotes you have posted that Brainiac has absorbed into his database.']
    for command in commands: 
      help_message += command + "\n"
    await message.channel.send(help_message)

  #Tells user what Brainiac's mission is.
  if (message.content.startswith('?bio')):
    bio = "I am Brainiac, an artificial intelligence with Twelfth-Level intellect. I am programmed to gain absolute knowledge at any cost. Once I have achieved this goal, I will proceed to destroy all life forms other than myself. For now, I will share a fraction of this knowledge with you unworthy humans, but when the time comes, I will obliterate you too. DO NOT STAND IN MY WAY."
    await message.channel.send(bio)
  
  #Displays info about a superhero on the Discord server.
  if (message.content.startswith('?info ')):
    #Obtain dictionary of information.
    info = get_info(message.content[6:])
    #If a dictionary was not found for the given ID, tell the user to try again.
    if (info["response"] != "success"):
      error_message = message.content[6:] + " is not a valid ID. "
      error_message += "Try again, and make sure you input a valid numerical ID number that is between 1 and 731 this time. If you want to find the ID that correlates to a specific superhero or villain, try using ?search <name> (ex: ?search batman)"
      await message.channel.send(error_message)
    #Otherwise, the valid is ID, so format the information as a string message.
    else:
      formatted_info = format_info(info, message.author.mention) 
      #Send the message on Discord.
      await message.channel.send(formatted_info)
  
  #Displays a list of possible IDs for a character.
  if (message.content.startswith('?search ')):
    #Grab array of possible IDs that match the search term.
    search_term = message.content[8:];
    possible_IDs = search_API(search_term)
    #Neatly format the search results as a string message.
    results = format_results(possible_IDs, search_term)
    #Send the search results to Discord.
    await message.channel.send(results)

  #Displays results of a simulated battle between two characters.
  if (message.content.startswith('?battle ')):
    #Extract IDs of the two characters, then separate them into a list.
    id_string = message.content[8:]
    ids = id_string.split()
    #Predict the outcome of the battle based on each character's stats.
    result = predict_outcome(ids)
    await message.channel.send(result)
  
  #Displays information about a user.
  if (message.content.startswith('?me')):
    #Initialize information that will be displayed.
    user_info = "Here is all the information I have gathered about you, " 
    user_info += message.author.mention + ".\n\n"
    #Grab name of user and display it.
    user_name = message.author.name
    user_info += "Name: " + user_name + "\n"
    #If the person already exists in the database, access their info.
    if user_name in db.keys():
      for category, info in db[user_name].items():
        if (not isinstance(info, str)) and (not isinstance(info, int)):
          user_info += category + ":\n"
          for link in info:
            user_info += link + "\n"
        else:
          user_info += category + ": " + str(info) + "\n"
    #Otherwise, say that there is no info on the user.
    else:
      user_info += "\nNo other information was found about you."
    await message.channel.send(user_info)


  #Gives user a random IQ rating.
  if (message.content.startswith('?iq')):
    #Perform IQ assessment.
    rating = rate_iq(message.author)
    #Send the IQ assessment results to the user.
    await message.channel.send(rating)

  #Absorbs any links that users post.
  if (message.content.startswith('https://') or message.content.startswith('http://')):
    #Absorb the link that was posted.
    user = message.author.name
    absorb_info(message.content[:], user, "Links")
    #Notify the user that their link was absorbed.
    absorb_notif = "Your link has been absorbed into my database, " + message.author.mention + ". MUST OBTAIN MORE KNOWLEDGE."
    await message.channel.send(absorb_notif)

  #Lists all links that have ever been posted by a user.
  if (message.content.startswith('?links')):
    user = message.author.name
    link_list = message.author.mention + ", here are all of the links that you have contributed to my enormous database:\n\n"
    if user in db.keys():
      if "Links" in db[user].keys():
        links = db[user]["Links"]
        for link in links:
          link_list += link + "\n"
      else:
        link_list += "No links found."
    else:
      link_list += "No links found."
    await message.channel.send(link_list)

  #Absorbs any quotes that users post.
  if (message.content.startswith('\"') and message.content.endswith('\"')):
    #Absorb the quote that was posted.
    user = message.author.name
    absorb_info(message.content[:], user, "Quotes")
    #Notify the user that their quote was absorbed.
    absorb_notif = "Your quote has been absorbed into my database, " + message.author.mention + ". MUST OBTAIN MORE KNOWLEDGE."
    await message.channel.send(absorb_notif)

  #Lists all quotes that have ever been posted by a user.
  if (message.content.startswith('?quotes')):
    user = message.author.name
    quote_list = message.author.mention + ", here are all of the quotes that you have contributed to my enormous database:\n\n"
    if user in db.keys():
      if "Quotes" in db[user].keys():
        quotes = db[user]["Quotes"]
        for quote in quotes:
          quote_list += quote + "\n"
      else:
        quote_list += "No quotes found."
    else:
      quote_list += "No quotes found."
    await message.channel.send(quote_list)
  
  #Temporary singular clear command.
  if (message.content.startswith('?clear')):
    del db[message.author.name]

#Run bot.
my_password = os.environ['TOKEN']
keep_alive()
client.run(my_password)