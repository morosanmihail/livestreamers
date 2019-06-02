import sys
import json
import random
import requests
import subprocess

OAUTH = 'OAuth <OAUTH HERE>'
FOLLOWED_FILE = '<PATH TO WHERE TO STORE FILE>.json'
FOLLOWED = ['<FOLLOWED STREAMS>']

url = 'https://api.twitch.tv/kraken/streams/followed'
client_id = 'dsv0rf69bvzgi9ch6ys16vwncjax1z'


def get_data():
    response = requests.get(
        url, headers={'Authorization': OAUTH, 'Client-ID': client_id}
    )
    data = json.loads(response.text)
    # Try to get stream info from json. Gives KeyError if the OAuth fails
    try:
        numStreams = data["_total"]
    except KeyError:
        print(formatting.RED + "KeyError - make sure your OAuth is formatted"
              "correctly in live.py" + formatting.ENDC)
        sys.exit(1)
    return data, numStreams


def save_online_streams(data):
    with open(FOLLOWED_FILE, 'w') as outfile:
        json.dump(data, outfile)


def load_online_streams():
    with open(FOLLOWED_FILE, 'r') as infile:
        text = infile.read()
    return text


def json_to_list(data, numStreams):
    streams = []
    for i in range(0, numStreams):
        channelName = data["streams"][i]["channel"]["name"]
        streams.append(channelName)
    return streams


print_one = sys.argv[1] if len(sys.argv) > 1 else None
print_one_val = sys.argv[2] if len(sys.argv) > 2 else None


class formatting:
    HEADER = "\033[95m"
    ENDC = "\033[0m"
    OKGREEN = "\033[92m"
    RED = "\033[91m"


data, numStreams = get_data()

if print_one == 'select':
    streams = json_to_list(data, numStreams)

    print(streams)

    def rofi_menu(streams, l=10):
        dmenu = subprocess.Popen(
            ['/usr/bin/rofi', '-i', '-l', str(l), '-dmenu', '-columns', '2', '-font', 'Noto Sans 14', '-width', '190'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        menu_str = '\n'.join(streams)
        # Popen.communicate returns a tuple stdout, stderr
        win_str = dmenu.communicate(menu_str.encode('utf-8'))[0].decode('utf-8').rstrip()
        return win_str

    stream = rofi_menu(streams)
    if stream:
        subprocess.Popen(["streamlink", "www.twitch.tv/" + stream, " best"])

if print_one == 'count':
    print(str(numStreams))
    if FOLLOWED:
        data_old = load_online_streams()
        data_new = json_to_list(data, numStreams)
        for stream in FOLLOWED:
            if stream in data_new and stream not in data_old:
                subprocess.Popen(["notify-send", "Stream online", stream])
        save_online_streams(data_new)

if print_one == 'random':
    print_one_val = print_one_val or 'name'
    index = random.randint(0, numStreams-1)
    print(data["streams"][index]["channel"][print_one_val])

if not print_one and not print_one_val:
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
