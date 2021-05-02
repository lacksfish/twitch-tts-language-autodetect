import os
import re
import vlc
import gtts
import socket
import tempfile
import configparser
from playsound import playsound
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

tempdir = tempfile.gettempdir()

player = vlc.Instance()
player.log_unset()

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
            # try:
                if "PRIVMSG" in resp:
                    username, channel, message = re.search(':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', resp).groups()

                    if username.lower() == ignore_user.lower():
                        print(f'Muted user not played: {ignore_user}')
                        continue

                    language = detect(message)

                    if len(message.split()) <= 3 and language not in ('en', 'de'):
                        language = 'en'

                    tts = gtts.gTTS(f'{username}      {message}', lang=language)
                    tts.save(tempdir + "\_last_twitch_chat_message.mp3")

                    if os.name == 'nt':
                        # Windows audio play
                        p = vlc.MediaPlayer(player, tempdir + "\_last_twitch_chat_message.mp3")
                        p.play()
                    else:
                        # Unix audio play
                        playsound(tempdir + "\_last_twitch_chat_message.mp3")


if __name__ == '__main__':
    main()
