import argparse
import json
import urllib.request

get_url = r'https://www.reddit.com/r/sixwordstories/top/.json?count=50&sort=top&t=all'
get_after_time = r'https://www.reddit.com/r/sixwordstories/top/.json?count=50&sort=top&t=all&after={0}'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download /r/sixwordstories data')
    parser.add_argument('--after', action="store", dest="after", type=str, default="", required=False, help="Download after given name.")
    parser.add_argument('--amount', action="store", dest="amount", type=int, default=5, required=False, help="Number of pages of 50 to download.")
    parser.add_argument('--out', action="store", dest="out", type=str, default="../corpus/reddit.json", required=False, help="Name of output file.")
    compiled_dict = {}
    compiled_dict["stories"] = []
    args = parser.parse_args()
    after = args.after
    for i in range(args.amount):
        if after == "":
            url = get_url
        else:
            url = get_url + '&after=' + after

        json_in = urllib.request.urlopen(url).read().decode('utf-8')
        dict_in = json.loads(json_in)
        for child in dict_in["data"]["children"]:
            data = child["data"]
            compiled_dict["stories"].append({"story":data["title"], "score":data["score"], "source":"REDDIT"})
        after = dict_in["data"]["after"]
        compiled_dict["last"] = after

    with open(args.out, "w") as f:
        json.dump(compiled_dict, f)
