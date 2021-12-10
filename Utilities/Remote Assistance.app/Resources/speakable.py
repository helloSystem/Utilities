#!/usr/bin/env python3

# Remote Assistance
# Copyright (c) 2021, Simon Peter <probono@puredarwin.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import requests
from requests.exceptions import HTTPError
import locale
import base64

from lxml.html.soupparser import fromstring


def make_speakable(payload):
    global headers, data, response, jsonResponse, http_err, err, speakable
    """
    Make a long Tox string easy to communicate over the phone
    by having something like
    "Gustav Nordpol Zacharias Theodor Gustav Theodor Kaufmann Gustav Ida Zacharias Berta Quelle"
    instead of
    "A2CA9A7C2AF065E3D99CA2D63147C43216A1130F43CC1F37AA020311F6A4691C57AA0AEACB24"
    """

    # If we were paranoid, we could encrypt the payload
    # cipher = AES.new(secret_key,AES.MODE_CTR, counter=Counter.new(128))
    try:
        headers = {
            'authority': 'url.api.stdlib.com',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (X11; FreeBSD amd64; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Falkon/3.1.0 Chrome/83.0.4103.122 Safari/537.36',
            'accept': '*/*',
            'dnt': '1',
        }
        data = '{"message":"' + payload + '","ttl":300}'
        response = requests.post('https://url.api.stdlib.com/temporary@0.3.0/messages/create/', headers=headers,
                                 data=data)
        response.raise_for_status()
        jsonResponse = response.json()
        # print("Entire JSON response")
        # print(jsonResponse)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    # Print each key-value pair from JSON response
    # for key, value in jsonResponse.items():
    #    print(key + ":", value)
    urldevkey = jsonResponse["key"].split("/")[1]
    encoded = base64.b32encode(urldevkey.encode("utf-8"))
    # print(encoded.decode("utf-8"))
    speakable = encoded.decode("utf-8").replace("=", "")
    # print(speakable)
    english = {
        'A': 'Alpha',
        'B': 'Bravo',
        'C': 'Charlie',
        'D': 'Delta',
        'E': 'Echo',
        'F': 'Foxtrot',
        'G': 'Golf',
        'H': 'Hotel',
        'I': 'India',
        'J': 'Juliet',
        'K': 'Kilo',
        'L': 'Lima',
        'M': 'Mike',
        'N': 'November',
        'O': 'Oscar',
        'P': 'Papa',
        'Q': 'Quebec',
        'R': 'Romeo',
        'S': 'Sierra',
        'T': 'Tango',
        'U': 'Uniform',
        'V': 'Victor',
        'W': 'Wiskey',
        'X': 'X-Ray',
        'Y': 'Yankee',
        'Z': 'Zulu',
        '1': 'One',
        '2': 'Two',
        '3': 'Tree',
        '4': 'Fower',
        '5': 'Fife',
        '6': 'Six',
        '7': 'Seven',
        '8': 'Eight',
        '9': 'Niner',
        '0': 'Zero'
    }
    german = {
        "A": "Anton",
        "B": "Berta",
        "C": "Cäsar",
        "D": "Dora",
        "E": "Emil",
        "F": "Friedrich",
        "G": "Gustav",
        "H": "Heinrich",
        "I": "Ida",
        "J": "Joseph",
        "K": "Kaufmann",
        "L": "Ludwig",
        "M": "Martha",
        "N": "Nordpol",
        "O": "Otto",
        "P": "Paula",
        "Q": "Quelle",
        "R": "Richard",
        "S": "Samuel",
        "T": "Theodor",
        "U": "Ulrich",
        "V": "Viktor",
        "W": "Wilhelm",
        "X": "Xanthippe",
        "Y": "Ypsilon",
        "Z": "Zacharias",
        '1': 'Eins',
        '2': 'Zwei',
        '3': 'Drei',
        '4': 'Vier',
        '5': 'Fünf',
        '6': 'Sechs',
        '7': 'Sieben',
        '8': 'Acht',
        '9': 'Neun',
        '0': 'Zehn'
    }
    # phonetic_alphabet_name_to_letter = {v : k for k, v in phonetic_alphabet_letter_to_name.iteritems()}
    spelling = ""
    for letter in speakable:
        if locale.getdefaultlocale()[0].startswith("de_"):
            spelling = spelling + " " + german[letter]
        else:
            spelling = spelling + " " + english[letter]
    spelling = spelling.strip()
    return(speakable, spelling)




def get_payload_from_speakable(speakable):
    global text, url, headers, response, http_err, err, data, jsonResponse
    text = speakable + "===="
    key = base64.b32decode(text.encode("utf-8")).decode("utf-8")
    url = "https://url.dev/m/" + key
    # print(url)
    try:
        headers = {
            'authority': 'url.api.stdlib.com',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (X11; FreeBSD amd64; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Falkon/3.1.0 Chrome/83.0.4103.122 Safari/537.36',
            'accept': '*/*',
            'dnt': '1',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # print(response.content)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    # Parse payload out of HTML
    tree = fromstring(response.content)
    payload = tree.xpath("/html/body/main/div['message']/p/text()")[0]
    # print(payload)
    try:
        headers = {
            'authority': 'url.api.stdlib.com',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (X11; FreeBSD amd64; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Falkon/3.1.0 Chrome/83.0.4103.122 Safari/537.36',
            'accept': '*/*',
            'dnt': '1',
        }
        data = '{"key":"m/' + key + '"}'
        response = requests.post('https://url.api.stdlib.com/temporary@0.3.0/destroy', headers=headers, data=data)
        response.raise_for_status()
        jsonResponse = response.json()
        # print(jsonResponse)
        if jsonResponse != True:
            print('Could not delete')
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    return(payload)

if __name__ == "__main__":
    speakable, spelling = make_speakable("A2CA9A7C2AF065E3D99CA2D63147C43216A1130F43CC1F37AA020311F6A4691C57AA0AEACB24")
    print("speakable: %s" % speakable)
    print("spelling: %s" % spelling)
    # Here would be the phone
    payload = get_payload_from_speakable(speakable)
    print("payload: %s" % payload)

