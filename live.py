import sys
import json
import random
import requests
import subprocess

url = 'https://api.twitch.tv/kraken/streams/followed'
oauth = 'OAuth <OAUTH HERE>'
client_id = 'dsv0rf69bvzgi9ch6ys16vwncjax1z'

response = requests.get(
    url, headers={'Authorization': oauth, 'Client-ID': client_id}
)
data = json.loads(response.text)
print_one = sys.argv[1] if len(sys.argv) > 1 else None
print_one_val = sys.argv[2] if len(sys.argv) > 2 else None


class formatting:
    HEADER = "\033[95m"
    ENDC = "\033[0m"
    OKGREEN = "\033[92m"
    RED = "\033[91m"


# Try to get stream info from json. Gives KeyError if the OAuth fails
try:
    numStreams = data["_total"]
except KeyError:
    print(formatting.RED + "KeyError - make sure your OAuth is formatted"
          "correctly in live.py" + formatting.ENDC)
    sys.exit(1)

if print_one == 'select':
    streams = []
    for i in range(0, numStreams):
        channelName = data["streams"][i]["channel"]["name"]
        streams.append(channelName)

    print(streams)

    def win_menu(streams, l=10):
        """
        Displays a window menu using dmenu. Returns window id.
        """
        dmenu = subprocess.Popen(
            ['/usr/bin/rofi', '-i', '-l', str(l), '-dmenu', '-columns', '3', '-font', 'Noto Sans 14', '-width', '190'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        menu_str = '\n'.join(sorted(streams))
        # Popen.communicate returns a tuple stdout, stderr
        win_str = dmenu.communicate(menu_str.encode('utf-8'))[0].decode('utf-8').rstrip()
        return win_str

    win_id = win_menu(streams)
    if win_id:
        subprocess.Popen(["streamlink", "www.twitch.tv/" + win_id, " best"])
    sys.exit(0)

if print_one == 'count':
    print(numStreams)
    sys.exit(0)

if print_one == 'random':
    print_one_val = print_one_val or 'name'
    index = random.randint(0, numStreams-1)
    print(data["streams"][index]["channel"][print_one_val])
else:
    for i in range(0, numStreams):
        channelName = data["streams"][i]["channel"]["name"]
        channelGame = data["streams"][i]["channel"]["game"]
        channelViewers = str(data["streams"][i]["viewers"])
        streamType = data["streams"][i]["stream_type"]

        # Check if stream is actually live or VodCast
        if(streamType == "live"):
            streamType = ""
        else:
            streamType = "(vodcast)"

        # Truncate long channel names/games
        if(len(channelName) > 18):
            channelName = channelName[:18] + ".."

        if(len(channelGame) > 38):
            channelGame = channelGame[:38] + ".."

        # Formatting
        print("{} {} {} {}".format(
            formatting.HEADER + channelName.ljust(20) + formatting.ENDC,
            channelGame.ljust(40),
            formatting.OKGREEN + channelViewers.ljust(8),
            formatting.RED + streamType + formatting.ENDC
            ))
