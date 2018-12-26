#!/usr/bin/python3.6
import discord
import random
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

# This is the token for the discord bot, you get this from the developer dashboard
token = ''

# Spotify api has different authorization scopes
# This scope gives us read access to the users private playlist
scope = 'playlist-read-private'

# User name URI, you get it from your profile, assign it
username = ''


# The URI for the specific spotify playlist you want to refer to, assign it.
list_id = ''

# Client ID which you get from spotify dev dashboard, assign it.
client_id = ''

# Client secret which you get from spotify dev dashboard, assign it.
client_sec = ''

# Whitelist a redirect uri, do this via spotify dashboard, i just chose a random link
redirect_uri = ''

# For making calls that need authorization
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_sec)

# Create an instance of the spotify client
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Returns the user token by prompting the user to login if it is needed
tokensp = util.prompt_for_user_token(username,scope,client_id= client_id,client_secret= client_sec, redirect_uri= redirect_uri)


def songs(username, list_id):
    """
    Function that goes through a users playlist and returns the songs name, a preview url and the artists name,
    as list of tuples.

    """
    # Gets the playlists songs
    result = sp.user_playlist_tracks(username, list_id)

    # Result is a dictionary and has a key called items, which holds the information we want.
    items = result["items"]

    # Create an empty list which will later on hold what we wish to return
    list_to_return = []

    # Iterate over the items data
    for value in items:

        #Value holds several keys, but the one we want is the track key
        val = value["track"]



        # We only want the name of the songs, preview urls and artist names
        # We get the songs name here
        song_name = val["name"]
        # Get the songs preview url here
        song_preview = val["preview_url"]

        # This returns a list of several elements that are relevant for the artist
        # but only the name element is important for us
        song_artists = val["artists"]

        # Iterate over the artists elements
        for index in song_artists:
            # Return only the artists names
            artist = index["name"]

        # The list contains a tupel of the song name, preview and artist name
        list_to_return.append((song_name, song_preview, artist))

    # list_to_return[elementIndex][tupelIndex]
    # elementIndex is a specific tupel which holds relevant information about a certain song, i.e name, preview url and artist name
    # tupelIndex is the different tupel indexes, which returns different information about a certain song
    # if tupelIndex = 0 you get Name, if tupelIndex = 1 you get preview_url, if tupelIndex = 2 you get artist name
    return list_to_return


# Create an instance of the discord client bot
client = discord.Client()

# Call the songs function and save it in a variable so we have all the playlists tracks
randSong = songs(username, list_id)



@client.event
async def on_reaction_add(reaction, user):
    """
    Bot client sending a message to the channel about what reaction was added on which message and by who.
    """
    # The reactions emoji
    emoji = reaction.emoji
    # The reaction on a message on the channel
    channel = reaction.message.channel
    if emoji is emoji:
        await client.send_message(channel, '{} has added {} to message {}'.format(user.name, emoji, reaction.message.content))


#Function for telling the server what a message was and what it was edited to
@client.event
async def on_message_edit(before, after):
    """
    If a message is edited the bot client will send a message telling which user edited a message from and to what it edited to.
    """
    # If a message is edited and the new message is different than the before we continue
    if after != before:
        channel = before.channel
        await client.send_message(channel, '{} has edited previous msg {} to {}'.format(before.author, before.content, after.content))


@client.event
async def on_member_update(before, after):
    """
    This function is based on memeber updates that occur on the channel of your choice.
    If a user changes its nickname the bot will send a message to the channel about the nick change.
    If a user starts playing a game or another app that is registered on discord the bot will send a message to the channel about the game.
    """
    # Gets the id of the channel sent in, this case my main channel
    id = client.get_channel('526362226978979843')

    # Changing of nicknames
    if after.nick != before.nick:
        # If you switch from your original name it will print our None to new_nick
        # therefore this statement should change so it only says what you change to
        if type(before.nick) is type(None):
            await client.send_message(id, 'Changed from their original nick to {}'.format(after.nick))
        #If you switch from a new to your original, so instead of printing None
        elif type(after.nick) is type(None):
            await client.send_message(id, "Changed nick from {} back to their original nick".format(before.nick))
        # Changing from a new before nick to an even newer
        else:
            await client.send_message(id, '{} changed name to {}'.format(before.nick, after.nick))

    # Changing of game status
    if after.game != before.game:
        # If the game status is no game at all it print None
        # to save us from the ugly None being printed this statement covers it
        if type(after.game) is type(None):
            await client.send_message(id, '{} quit playing {}'.format(before.nick, before.game))
        else:
            await client.send_message(id, '{} started playing {}'.format(before.nick, after.game))



@client.event
async def on_message(message):
    """
    This function holds on several different message contents that the bot will react to.
    """

    # If the content of a message starts with !hello or !Hello
    if message.content.startswith("!hello") or message.content.startswith("!Hello"):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    # If the content of a message starts with !Commands or !commands
    if message.content.startswith("!Commands") or message.content.startswith("!commands"):
        msg = "Here are the commands {0.author}: !song, !hello, !react".format(message)
        await client.send_message(message.channel, msg)

    # If the content of a message starts with !Song or !song
    if message.content.startswith("!Song") or message.content.startswith("!song"):
        # Reasong for having the random song index here is because
        # if you have it ourside it will be set to a specific random number
        # and stay as that index everytime Song command is run
        # we want a new random index everytime this command is run
        # therefore we randomize whenever the command is called
        random_song_index = random.randint(0, 50)

        # Some songs do not have a preview_url so this case is for those songs
        if type(randSong[random_song_index][1]) is type(None):
            # Send a message containing song name and artist name, but no preview url
            msg = "Here is a song tip " + randSong[random_song_index][0] +  ' by: ' + randSong[random_song_index][2] + '. Unfortunately the song does not have any preview'
            await client.send_message(message.channel, msg)

        # If the song does have a previes_url so we can send it as well in the message
        else:
            msg = 'Here is a song tip: ' + randSong[random_song_index][0] + ' by: ' + randSong[random_song_index][2] + '. Link: ' + randSong[random_song_index][1]
            await client.send_message(message.channel, msg)

    # If the content of a message starts with !React or !react, bot will react with a set emoji.
    if message.content.startswith("!React") or message.content.startswith("!react"):
        await client.add_reaction(message, u"\U0001F525")

    # All messages that contain the word "what" the bot will send a message accordingly.
    # To be changed later, just did this because wanted to see if it worked like i thought
    if "what"  in message.content:
        msg = "Did you say the secret word".format(message)
        await client.send_message(message.channel, msg)



@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


# Run the client with your token
client.run(token)
