import requests
from bs4 import BeautifulSoup

# how to install:
# python3 -m pip install virtualenv
# python3 -m virtualenv virtualenv
# source virtualenv/activate
# python3 -m pip install requests beautifulsoup4

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
google_url = "https://www.google.com/search?hl=en_US"
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
query = "the office cast" # OK

print("Question: ", query)

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
        print("* ", element.div.text, " = ", element.div.next_sibling.text)

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
    print("answer: ", lyrics.text)

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
