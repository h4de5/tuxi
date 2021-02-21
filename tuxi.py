#!/usr/bin/env python3
# vim: set fileencoding=utf8 :

import sys, getopt, locale
import requests
import textwrap
from bs4 import BeautifulSoup


###############################
#####      Constants      #####
###############################

LANGUAGE = ""


def help_text():
    print("%sUsage:%s tuxi %s[options]%s %squery%s" % (G, N, Y, N, M, N))
    print("")
    print("%sOptions:%s" % (G, N))
    print("  -h                    Show this help message and exit.")
    print("  -r                    Raw search results.")
    print("                        (no pretty output, no colors)")
    print("  -q                    Only output search results.")
    print("                        (silences \"Did you mean?\", greeting, usage)")
    print("  -l                    Language ISO Code - e.g. en_US or de_DE.")
    print("  -a                    Return all matching result types.")
    print("")
    print("%sReport bugs at%s %shttps://github.com/h4de5/tuxi/issues%s" % (G, N, C, N))

# Checks if dependencies are installed.
# check_deps():
#     while [ -n "$1" ]; do
#         if [ ! "$(command -v $1)" ]; then
#             error_msg "\"$1\" not found!"
#             exit 2
#         fi
#         shift
#     done


def info_msg(*message):
    print("%s>%s %s" % (G, N, ''.join(message)))


def error_msg(*message):
    print("%s%s%s" % (R, ''.join(message), N))


#############################
##### Dependency check  #####
#############################

# pup : https://github.com/ericchiang/pup
# recode : https://github.com/rrthomas/recode
# jq : https://github.com/stedolan/jq
# check_deps "pup" "recode" "jq"


###############################
#####       Defaults      #####
###############################

# system language fallback
LANG, encoding = [LANGUAGE, 'UTF-8'] if LANGUAGE else locale.getdefaultlocale()

# color codes
N = "\033[0m"     # Reset
R = "\033[1;31m"  # Red
G = "\033[1;32m"  # Green
Y = "\033[1;33m"  # Yellow
M = "\033[1;35m"  # Magenta
C = "\033[1;36m"  # Cyan

# options
raw = False
quiet = False
allresults = False
query = []


# search result output format (changes if raw=true)
def output(*message):
    global raw
    if raw:
        print(''.join(message))
    else:
        print("%s---%s\n%s\n%s---%s" % (G, N, ''.join(message), G, N))
    if not allresults:
        exit(0)


#############################
#####     Getopts       #####
#############################

# -h : help
# -r : raw search result
# -q : silences greeting and did you mean
def getopts(argv):
    global raw, quiet, query, allresults, LANG
    try:
        opts, args = getopt.getopt(argv, "hrqal:")
    except getopt.GetoptError:
        help_text()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help_text()
            sys.exit()
        elif opt == '-r':
            raw = True
        elif opt == '-q':
            quiet = True
        elif opt == '-a':
            allresults = True
        elif opt == '-l':
            LANG = arg

    query = ' '.join(args).strip()


if __name__ == "__main__":
    getopts(sys.argv[1:])

#############################
#####   Raw formatting  #####
#############################

# If raw=true: No colors, No pretty output
if raw:
    N = R = G = Y = M = C = ""

#############################
#####    Query check    #####
#############################

# If query is empty: exit
# If quiet=false: Prints greeting and usage
if not query:
    if not quiet:
        print("Hi, I'm Tuxi. Ask me anything!")
        help_text()
    exit(0)


# Else, all arguments are saved in $query
# already done
# query="$*"

##############################
##### Snippet extraction #####
##############################

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
google_url = "https://www.google.com/search?hl=" + LANG

# Response from Google via cURL (-G: get, -s: silent)
# google_html=$(curl -Gs --compressed "$google_url" --user-agent "$user_agent" --data-urlencode "q=$query")
google_html_raw = requests.get(google_url, params={'q': query}, headers={'user-agent': user_agent})
google_html = BeautifulSoup(google_html_raw.text, "html.parser")

## Snippet Priority ##
# Did you mean
# Math
# Knowledge Graph - top
# Basic Answers
# Rich Answers
# Featured Snippets
# Lyrics
# Weather
# Units Convertion
# Currency Convertion
# Translate
# Knowledge Graph - right

# did you mean ( eg: linux torvalds ) Because we all know his real name is linux, not linus.
# silenced if quiet=true
# if [ $quiet = "false" ]; then
#     did_you_mean="$(echo "$google_html" | pup 'a.gL9Hy > b text{}' | sed ':a;N;$!ba;s/\n/ /g' | recode html..ISO-8859-1)"
#     [ -n "$did_you_mean" ] && info_msg "Did you mean $did_you_mean?"
# fi
if not quiet:
    did_you_mean = google_html.find("a", class_="gL9Hy")
    if did_you_mean:
        info_msg("Did you mean %s?" % did_you_mean.text)

# # Math ( eg: log_2(3) * pi^e )
# math="$(echo "$google_html" | pup 'span.qv3Wpe text{}' | tr -d '\n ' | recode html..ISO-8859-1)"
# [ -n "$math" ] && output "$math" && exit 0
math = google_html.find("span", class_="qv3Wpe") or google_html.find("div", class_="vrBOv") or google_html.find("div", class_="ikb4Bb")
math and output(math.text)


# # Knowledge Graph - top (list) ( eg: the office cast, us presidents )
# kno_top=$(echo "$google_html" | pup 'div.dAassd json{}'  | jq -r '.[] | .children | .[] | .text' | sed ':a;N;$!ba;s/\n/ /g' | sed 's/null/\n/g' | awk '{$1=$1;print "* " $0}' | sed '/^* $/d'| recode html..ISO-8859-1)
# [ -n "$kno_top" ] && output "$kno_top" && exit 0
kno_top = google_html.find_all("div", class_="dAassd")
if kno_top:
    result = ""
    for element in kno_top:
        # print("children:", element.contents)
        result += "\n* "
        for subelement in element.contents:
            if subelement["class"] == ["cp7THd"]:
                result += " (" + subelement.text + ")"
            else:
                result += subelement.text.strip() + " "
    result and output(result.strip())


# # Basic Answers ( eg: tuxi christmas day )
# basic="$(echo "$google_html" | pup 'div.zCubwf text{}' | tr -d '\n' | recode html..ISO-8859-1)"
# [ -n "$basic" ] && output "$basic" && exit 0
basic = google_html.find("div", class_="zCubwf")
basic and output(basic.text)


# # Rich Answers ( eg: elevation of mount everest )
# rich=$(echo "$google_html" | pup 'div.XcVN5d text{}' | recode html..ISO-8859-1)
# [ -n "$rich" ] && output "$rich" && exit 0
rich = google_html.find("div", class_="XcVN5d")
rich and output(rich.text)


# # Featured Snippets ( eg: who is garfield )
# feat="$(echo "$google_html" | pup 'span.hgKElc text{}' | tr -d '\n' | recode html..ISO-8859-1 | tr ' ' '\0' | xargs -0 -n10)"
# [ -n "$feat" ] && output "$feat" && exit 0
feat = google_html.find("span", class_="hgKElc")
feat and output(textwrap.fill(feat.text))


# # Lyrics ( eg: gecgecgec lyrics )
# lyrics="$(echo "$google_html" | pup 'div.bbVIQb text{}' | recode html..ISO-8859-1)"
# [ -n "$lyrics" ] && output "$lyrics" && exit 0
# #Lyrics for US users, above does not work for US
# lyrics="$(echo "$google_html" | pup 'span[jsname="YS01Ge"] text{}' | recode html..ISO-8859-1)"
# [ -n "$lyrics" ] && output "$lyrics" && exit 0
lyrics = google_html.find("div", class_="bbVIQb")
if lyrics:
    lyrics2 = lyrics.find_all("span")
    result = ""
    for element in lyrics2:
        result += element.text + "\n"
    result and output(result.strip())


# # Weather ( eg: weather new york)
# weather="$(echo "$google_html" | pup 'div.UQt4rd json{}' | jq -r '.. | .text?, .alt?'| sed '/null/d' |  sed '$!N; /^\(.*\)\n\1$/!P; D' | sed '4,5d;2s/.*/&ºC/;2,${N;s/\n/\t/;};3s/.*/&ºF/;$s/\t/\t\t/' | recode html..ISO-8859-1)"
# [ -n "$weather" ] && output "$weather" && exit 0
# TODO
weather = google_html.find("div", class_="UQt4rd")
if weather:
    weather2 = weather.find_all("span", class_="wob_t")
    result = ""
    for element in weather2:
        if "style" not in element or element["style"].find("display:none") == -1:
            result += element.text + " "
    result and output(result.strip())
# weather and print(weather.prettify())  # output(weather.contents)

weather = google_html.find("span", class_="vk_gy")
weather and output(weather.text)


# # Units Conversion ( eg: 1m into 1 cm, 35 euro to bitcoin, (30l * 40h) / 0.2l/min)
# unit="$(echo "$google_html" | pup '#NotFQb json{}' | jq -r '.[] | .children | .[0] | .value' | recode html..ISO-8859-1)"
# [ -n "$unit" ] && output "$unit" && exit
unit = google_html.find("", id="NotFQb")
unit and output(unit.text)
unit = google_html.find_all("input", class_="vXQmIe")
unit and output(unit[1]["value"])


# # Currency Conversion ( eg: 1 USD in rupee )
# currency="$(echo "$google_html" | pup '.SwHCTb text{}' | tr -d '\n' | tr ' ' '\0' | recode html..ISO-8859-1)"
# [ -n "$currency" ] && output "$currency" && exit
currency = google_html.find("", id="SwHCTb")
currency and output(currency.text)


# # Translate ( eg: Vais para cascais? em ingles, what is thank you in italian)
# trans="$(echo "$google_html" | pup 'pre.XcVN5d json{}' | jq -r '[.[] | .children | .[] | select(.class!="BCGytf")][1] | .text' | sed 's/null//g' | recode html..ISO-8859-1)"
# [ -n "$trans" ] && output "$trans" && exit
trans = google_html.find("div", class_="g9WsWb")
if trans:
    trans2 = trans.find("pre", class_="XcVN5d")
    trans2 and output(trans2.text)


# # Knowledge Graph - right ( eg: the office )
# kno_right="$(echo "$google_html" | pup 'div.kno-rdesc span' | sed -n '2p' | awk '{$1=$1;print}' | recode html..ISO-8859-1 | tr ' ' '\0' | xargs -0 -n10)"
# [ -n "$kno_right" ] && output "$kno_right" && exit 0
kno_right = google_html.find("div", class_="kno-rdesc")
if kno_right:
    kno_right = kno_right.find("span")
    kno_right and output(kno_right.text)


# does not work, because result is set in javascript
random = google_html.find_all("div", class_="PmF7Ce")
if random:
    result = ""
    for element in random:
        if element["aria-hidden"] == "false":
            result += element.text
    random and output(random)

# Else
if not allresults:
    error_msg("No Result!")
    exit(1)