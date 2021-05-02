import os
import re
import vlc
import time
import gtts
import socket
import tempfile
import configparser
from playsound import playsound
from textblob import TextBlob as TB

#                __
#               / _)
#      _/\/\/\_/ /
#    _|         /
#  _|  (  | (  |
# /__.-'|_|--|_|
# You have been visited by code dino,
# you shall receive eternal luck. ⊂(◉‿◉)つ


# Get temp dir for audio files
tempdir = tempfile.gettempdir()

# Init VLC media player - windows only
if os.name == 'nt':
    player = vlc.Instance()
    player.log_unset()

# Read config from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

oauth = config['DEFAULT']['oauth_token']
twitch_username = config['DEFAULT']['twitch_username']
ignore_user = config['DEFAULT']['ignore_user']


def main():
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = twitch_username
    token = oauth
    channel = f'#{twitch_username}'

    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    print('\n\nConnecting...')
    connected = False

    while True:
        resp = sock.recv(2048).decode('utf-8')

        if resp and not connected:
            print(f'Connected to {nickname}!')
            connected = True

        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))

        elif len(resp) > 0:
                # If it is a user chat message
                if "PRIVMSG" in resp:
                    username, channel, message = re.search(':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', resp).groups()

                    if username.lower() == ignore_user.lower():
                        print(f'Muted user not played: {ignore_user}')
                        continue

                    # Detect language of chat message
                    text = TB(message)
                    language = text.detect_language()

                    # If it is a very short message and it's neither german nor english, just stick with english
                    # if len(message.split()) <= 3 and language not in ('en', 'de'):
                    #     language = 'en'

                    # Create and save TTS mp3 file in temp folder
                    # Try with detected language, otherwise just use english as a failsafe
                    try:

                        tts = gtts.gTTS(f'{username}      {message}', lang=language)
                    except:
                        tts = gtts.gTTS(f'{username}      {message}', lang='en')
                    tts.save(tempdir + "\_last_twitch_chat_message.mp3")

                    # Play audio depending on operating system
                    if os.name == 'nt':
                        # Windows audio play
                        p = vlc.MediaPlayer(player, tempdir + "\_last_twitch_chat_message.mp3")
                        p.play()
                        # Actually wait for audio file to finish playing - jesus
                        # https://stackoverflow.com/a/49185960
                        time.sleep(1.5)
                        duration = p.get_length() / 1000
                        time.sleep(duration)
                    else:
                        # Unix audio play
                        playsound(tempdir + "\_last_twitch_chat_message.mp3")


if __name__ == '__main__':
    main()
