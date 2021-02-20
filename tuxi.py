#!/usr/bin/env python
# vim: set fileencoding=utf8 :

import sys, getopt, locale
import requests
from bs4 import BeautifulSoup


###############################
#####      Constants      #####
###############################

LANGUAGE = "de_DE"


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


def info_msg(message):
    print("%s>%s %s" % (G, N, message))


def error_msg(message):
    print("%s%s%s" % (R, message, N))


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
query = []


# search result output format (changes if raw=true)
def output(message):
    global raw
    if raw:
        print(message)
    else:
        print("%s---%s\n%s\n%s---%s" % (G, N, message, G, N))


#############################
#####     Getopts       #####
#############################

# -h : help
# -r : raw search result
# -q : silences greeting and did you mean
def getopts(argv):
    global raw, quiet, query, LANG
    try:
        opts, args = getopt.getopt(argv, "hrql:")
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
        elif opt == '-l':
            LANG = arg

    query = ' '.join(args).strip()


if __name__ == "__main__":
    getopts(sys.argv[1:])

    # print("parameters: ", sys.argv[1:])
    # print("raw:", raw)
    # print("quiet:", quiet)
    # print("found question: ", query)

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

print("language", LANG)

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

# # Knowledge Graph - top (list) ( eg: the office cast )
# kno_top=$(echo "$google_html" | pup 'div.dAassd json{}'  | jq -r '.[] | .children | .[] | .text' | sed ':a;N;$!ba;s/\n/ /g' | sed 's/null/\n/g' | awk '{$1=$1;print "* " $0}' | sed '/^* $/d'| recode html..ISO-8859-1)
# [ -n "$kno_top" ] && output "$kno_top" && exit 0


# # Basic Answers ( eg: tuxi christmas day )
# basic="$(echo "$google_html" | pup 'div.zCubwf text{}' | tr -d '\n' | recode html..ISO-8859-1)"
# [ -n "$basic" ] && output "$basic" && exit 0


# # Rich Answers ( eg: elevation of mount everest )
# rich=$(echo "$google_html" | pup 'div.XcVN5d text{}' | recode html..ISO-8859-1)
# [ -n "$rich" ] && output "$rich" && exit 0


# # Featured Snippets ( eg: who is garfield )
# feat="$(echo "$google_html" | pup 'span.hgKElc text{}' | tr -d '\n' | recode html..ISO-8859-1 | tr ' ' '\0' | xargs -0 -n10)"
# [ -n "$feat" ] && output "$feat" && exit 0


# # Lyrics ( eg: gecgecgec lyrics )
# lyrics="$(echo "$google_html" | pup 'div.bbVIQb text{}' | recode html..ISO-8859-1)"
# [ -n "$lyrics" ] && output "$lyrics" && exit 0


# # Weather ( eg: weather new york)
# weather="$(echo "$google_html" | pup 'div.TylWce text{}' | sed -e '1 s/$/ ºC/' -e '2 s/$/ ºF/' | recode html..ISO-8859-1)"
# [ -n "$weather" ] && output "$weather" && exit 0


# # Units Conversion ( eg: 1m into 1 cm )
# unit="$(echo "$google_html" | pup '#NotFQb json{}' | jq -r '.[] | .children | .[0] | .value' | recode html..ISO-8859-1)"
# [ -n "$unit" ] && output "$unit" && exit


# # Currency Conversion ( eg: 1 USD in rupee )
# currency="$(echo "$google_html" | pup '.SwHCTb text{}' | tr -d '\n' | tr ' ' '\0' | recode html..ISO-8859-1)"
# [ -n "$currency" ] && output "$currency" && exit


# # Translate ( eg: Vais para cascais? em ingles )
# trans="$(echo "$google_html" | pup 'pre.XcVN5d json{}' | jq -r '[.[] | .children | .[] | select(.class!="BCGytf")][1] | .text' | sed 's/null//g' | recode html..ISO-8859-1)"
# [ -n "$trans" ] && output "$trans" && exit


# # Knowledge Graph - right ( eg: the office )
# kno_right="$(echo "$google_html" | pup 'div.kno-rdesc span' | sed -n '2p' | awk '{$1=$1;print}' | recode html..ISO-8859-1 | tr ' ' '\0' | xargs -0 -n10)"
# [ -n "$kno_right" ] && output "$kno_right" && exit 0


# Else
# error_msg "No Result!" && exit 1


exit(0)

# how to install:
# python3 -m pip install virtualenv
# python3 -m virtualenv virtualenv
# source virtualenv/bin/activate
# python3 -m pip install requests beautifulsoup4

# DID YOU MEAN
# query = "how old is linux torvalds"

# TRANSLATE
# query = "what is thank you in italian" # OK <pre class="tw-data-text tw-text-large XcVN5d tw-ta" data-placeholder="Translation" id="tw-target-text" style="text-align:left"><span lang="it">grazie</span></pre>
# query = "Vais para cascais? em ingles" # OK

# MATH
# query = "35 euro to bitcoin" # OK <div class="dDoNo ikb4Bb vk_bk gsrt gzfeS"><span class="DFlfde SwHCTb" data-precision="5" data-value="8.0512905095E-4">0,00081</span> <span class="MWvIVe" data-mid="/m/05p0rrx" data-name="Bitcoin">Bitcoin</span></div>
# query = "(30l * 40h) / 0.2l/min" # OK <div class="dDoNo vrBOv vk_bk">2.38538521 × 10<sup>-28</sup> m<sup>2</sup> kg</div>
# query = "log_2(3) * pi^e" # OK <span jsname="VssY5c" class="qv3Wpe" id="cwos">35.5969227814</span>

# RANDOM
# query = "flip a coin" # <div jsname="DyVWtc" class="PmF7Ce" aria-hidden="true">Heads</div>
# query = "roll a dice" #

# WEATHER
# query = "how is the weather in london" # OK <span class="vk_gy vk_sh" id="wob_dc">Clear with periodic clouds</span>

# KNOWLEDGE GRAPH
# query = "the office cast" # OK

# query = "wie alt ist linux torvalds"

# print("Question: ", query)

headers = {'user-agent': user_agent}

# Response from Google via cURL (-G: get, -s: silent)
# google_html=$(curl -Gs --compressed "$google_url" --user-agent "$user_agent" --data-urlencode "q=$query")

## Snippet Priority ##
# Did you mean
# Math
# Knowledge Graph - top
# ?
# Rich Answers
# Featured Snippets
# Google Translate
# Lyrics
# Knowledge Graph - right

google_html = requests.get(google_url, params={'q': query}, headers=headers)
html = BeautifulSoup(google_html.text, "html.parser")

did_you_mean = html.find("a", class_="gL9Hy")
if did_you_mean:
    query = did_you_mean.text
    print("did you mean: ", query)
    google_html = requests.get(google_url, params={'q': query}, headers=headers)
    html = BeautifulSoup(google_html.text, "html.parser")

math = html.find("span", class_="qv3Wpe") or html.find("div", class_="vrBOv") or html.find("div", class_="ikb4Bb")
if math:
    print("math answer: ", math.text)

rich = html.find("div", class_="XcVN5d") or (html.find("div", class_="g9WsWb") and html.find("div", class_="g9WsWb").find("pre", class_="XcVN5d"))
if rich:
    print("rich answer: ", rich.text)

# # Google Translate ( eg: Vais para cascais? em ingles )
# trans="$(echo "$google_html" | pup 'pre.XcVN5d json{}' | jq -r '[.[] | .children | .[] | select(.class!="BCGytf")][1] | .text' | recode html..ISO-8859-1)"
# [ -n "$trans" ] && output "$trans" && exit

# # Rich Answers ( eg: elevation of mount everest )
# rich=$(echo "$google_html" | pup 'div.XcVN5d text{}' | recode html..ISO-8859-1)
# [ -n "$rich" ] && output "$rich" && exit 0

feat = html.find("span", class_="hgKElc")
if feat:
    print("feat answer: ", feat.text)

# # Featured Snippets ( eg: who is garfield )
# feat="$(echo "$google_html" | pup 'span.hgKElc text{}' | tr -d '\n' | recode html..ISO-8859-1 | tr ' ' '\0' | xargs -0 -n10)"
# [ -n "$feat" ] && output "a$feat" && exit 0

kno_top = html.find_all("div", class_="dAassd")
if kno_top:
    print("knot answer: ")
    for element in kno_top:
        print("* ", element.div.text, "..", element.div.next_sibling.text)

# # Knowledge Graph - top (list) ( eg: the office cast )
# kno_top=$(echo "$google_html" | pup 'div.dAassd json{}'  | jq -r '.[] | .children | .[] | .text' | sed ':a;N;$!ba;s/\n/ /g' | sed 's/null/\n/g' | awk '{$1=$1;print "* " $0}' | sed '/^* $/d'| recode html..ISO-8859-1)
# [ -n "$list" ] && output "$kno_top" && exit 0


res1 = html.find("div", class_="zCubwf")
if res1:
    print("answer: ", res1.text)

# # ?
# res1="$(echo "$google_html" | pup 'div.zCubwf text{}' | tr -d '\n' | recode html..ISO-8859-1)"
# [ -n "$res1" ] && output "$res1" && exit 0

lyrics = html.find("div", class_="bbVIQb")
if lyrics:
    print("lyrics answer: ", lyrics.text)

# # Lyrics ( eg: gecgecgec lyrics )
# lyrics="$(echo "$google_html" | pup 'div.bbVIQb text{}' | recode html..ISO-8859-1)"
# [ -n "$lyrics" ] && output "$lyrics" && exit 0

kno_right = html.find("div", class_="kno-rdesc") and html.find("div", class_="kno-rdesc").find("span")
if kno_right:
    print("knor answer: ", kno_right.text)
    # for element in kno_right:
    #     print("knor answer: ", element.span.text)

# # Knowledge Graph - right ( eg: the office )
# kno_right="$(echo "$google_html" | pup 'div.kno-rdesc span' | sed -n '2p' | awk '{$1=$1;print}' | recode html..ISO-8859-1 | tr ' ' '\0' | xargs -0 -n10)"
# [ -n "$kno_right" ] && output "$kno_right" && exit 0


weather = html.find("span", class_="vk_gy")
if weather:
    print("weather answer: ", weather.text)
