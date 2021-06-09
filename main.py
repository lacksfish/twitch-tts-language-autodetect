import os
import re
import time
import gtts
import emoji
import socket
import tempfile
import configparser

## SUGGESTION 1 translate "says"
from translate import Translator

##SUGGESTION 2 control playback speed (requires ffmpeg)
from pydub import AudioSegment
from pydub import effects

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
from logger import get_logger, init_message
from pathlib import Path
from playsound import playsound
from textblob import TextBlob as TB

init_message()

# Init audio for windows
if os.name == 'nt':
    mixer.init()

# Get temp dir for audio files
tempdir = tempfile.gettempdir() + '\diy_TTS'
Path(tempdir).mkdir(parents=True, exist_ok=True)

# Read config from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

oauth = config['DEFAULT']['oauth_token']
twitch_username = config['DEFAULT']['twitch_username']
ignore_user = config['DEFAULT']['ignore_user']
logfile = config['DEFAULT']['logfile']

##SUGGESTION 2
playback_speed = config['DEFAULT']['playback_speed']

##SUGGESTION 3 choose a list of languages (include all in list if all languages should be covered)
languages = config['DEFAULT']['languages']
languages_list = languages.replace(" ","").split(",")

# Init message logs
log = get_logger('MAIN', create_file=logfile)


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

    log.info('Connecting to chat...')
    connected = False

    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')

            if not connected:
                if len(resp) > 0:
                    log.info(f'Connected to {twitch_username}!')
                    connected = True

            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            elif len(resp) > 0:
                # If it is a user chat message
                if "PRIVMSG" in resp:
                    username, channel, message = re.search(':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', resp).groups()

                    if username.lower() == ignore_user.lower():
                        log.info(f'Muted user not played: {ignore_user}')
                        continue
                    log.info(f'New message from {username}: {emoji.demojize(message)}')

                    # Delete old temp message mp3's
                    for f in os.listdir(tempdir):
                        try:
                            os.remove(os.path.join(tempdir, f))
                        except:
                            pass

                    # Detect language of chat message, use english as failsafe
                    try:
                        text = TB(message)
                        language = text.detect_language()
                    except:
                        language = 'en'
                    
                    ##SUGGESTION 3
                    if language not in languages_list and "all" not in languages_list:
                        language = 'en'
					
                    ##SUGESTION 1 START
                    translator= Translator(to_lang=language,from_lang="en")
                    says = translator.translate("says")
                    if  "IS AN INVALID TARGET LANGUAGE" in says :
                        says = ":"

                    # Try speaking with detected language, use english as a failsafe
                    try:
                        tts = gtts.gTTS(f'{username}{says} {message}', lang=language)
                    except:
                        tts = gtts.gTTS(f'{username}: {message}', lang='en')
                    ##SUGESTION 1 END
                    
                    # Create and save TTS mp3 file in temp folder
                    tempfile_name = next(tempfile._get_candidate_names())
                    tts.save(tempdir + f'\{tempfile_name}.mp3')
                    
                    ##SUGGESTION 2
                    if playback_speed != 1:
                        sound = AudioSegment.from_file(tempdir + f'\{tempfile_name}.mp3')
                        so = sound.speedup(playback_speed, 150, 25)
                        tempfile_name = tempfile_name + str(playback_speed)
                        so.export(tempdir + f'\{tempfile_name}.mp3', format = 'mp3')

                    # Play audio depending on operating system
                    if os.name == 'nt':
                        # Wait on previous message
                        while mixer.music.get_busy():
                            time.sleep(0.5)
                        # Unload old messages
                        mixer.music.unload()
                        # Windows audio play
                        mixer.music.load(tempdir + f'\{tempfile_name}.mp3')
                        mixer.music.play()
                    else:
                        # Unix audio play
                        playsound(tempdir + f'\{tempfile_name}.mp3')
        except Exception as e:
            log.error(str(e))
            connected = False
            sock.close()
            while not connected:
                try:
                    sock = socket.socket()
                    sock.connect((server, port))
                    sock.send(f"PASS {token}\n".encode('utf-8'))
                    sock.send(f"NICK {nickname}\n".encode('utf-8'))
                    sock.send(f"JOIN {channel}\n".encode('utf-8'))
                    connected = True
                    log.info(f'Reconnected to {twitch_username}!')
                except:
                    log.error('Not connected, reconnecting ...')
                time.sleep(5)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
