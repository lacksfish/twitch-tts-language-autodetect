import os
import re
import gtts
import socket
import tempfile
import configparser
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

# Init message logs
log = get_logger('MAIN')

# Get temp dir for audio files
tempdir = tempfile.gettempdir() + '\diy_TTS'
Path(tempdir).mkdir(parents=True, exist_ok=True)

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

    print('Connecting to chat...')
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
                        log.info(f'Muted user not played: {ignore_user}')
                        continue
                    log.info(f'New message from {username}: {message}')

                    # Delete old temp message mp3's
                    mixer.music.unload()
                    for f in os.listdir(tempdir):
                        try:
                            os.remove(os.path.join(tempdir, f))
                        except:
                            pass

                    # Detect language of chat message
                    text = TB(message)
                    language = text.detect_language()

                    # Create and save TTS mp3 file in temp folder
                    # Try with detected language, otherwise just use english as a failsafe
                    try:
                        tts = gtts.gTTS(f'{username}: {message}', lang=language)
                    except:
                        tts = gtts.gTTS(f'{username}: {message}', lang='en')
                    tempfile_name = next(tempfile._get_candidate_names())
                    tts.save(tempdir + f'\{tempfile_name}.mp3')

                    # Play audio depending on operating system
                    if os.name == 'nt':
                        # Windows audio play
                        mixer.music.load(tempdir + f'\{tempfile_name}.mp3')
                        mixer.music.play()
                    else:
                        # Unix audio play
                        playsound(tempdir + f'\{tempfile_name}.mp3')


if __name__ == '__main__':
    main()
