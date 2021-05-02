import gtts
import socket
import re
from playsound import playsound
from langdetect import detect
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

oauth = config['DEFAULT']['oauth_token']
username_twitch = config['DEFAULT']['twitch_username']


def main():
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = username_twitch
    token = oauth
    channel = f'#{username_twitch}'

    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    while True:
        resp = sock.recv(2048).decode('utf-8')

        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))

        elif len(resp) > 0:
            try:
                username, channel, message = re.search(':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', resp).groups()

                language = detect(message)

                tts = gtts.gTTS(f'{username}      {message}', lang=language)
                tts.save("_last.mp3")
                playsound("_last.mp3")
            except:
                pass


if __name__ == '__main__':
    main()
