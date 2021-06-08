from io import FileIO
from typing import Tuple
from typing import TypedDict

import sys
import os
import requests
import time
from PIL import Image


class S3Fields(TypedDict):
    key: str
    AWSAccessKeyId: str
    policy: str
    signature: str


# I'm not sure if this token is unique to my phone or the one request I
# reverse-engineered this from, but I do know that you can reuse them, so this
# can just stay hard-coded
TOKEN = "d29tYm8tdGhhdC1zaGl6ejpHZXRUaGF0QnJlYWQkMSE="

# User-readable dictionary of IDs of memes Wombo can make
MEMES = {
    "rickroll": 1,
    "numa-numa": 2,
    "boom": 3,
    "dreams": 4,
    "baka-mitai": 5,
    "i-feel-good": 6,
    "witch-doctor": 7,
    "everytime-we-touch": 8,
    "i-will-survive": 9,
    "dont-cha": 10,
    "tralala": 11,
    "thriller": 12,
    "bitch": 13,
    "i-will-always-love-you": 14,
    "happy-birthday": 22,
    "entertainer": 23,
    "rockin-robin": 24,
    "rising-sun": 25,
    "periodic-table": 26,
    "were-not-gonna": 31,
    "all-star": 32,
    "what-is-love": 33,
    "fortnite": 34,
    "hino-da-sociedade": 35,
    "dame-tu-cosita": 36,
    "tunak-tunak-tun": 37,
    "bande-organisee": 38,
    "ymca": 39,
    "funkytown": 40,
    "bing-bong": 41,  # premium
    "whats-going-on": 42,
    "take-on-me": 43,  # premium
    "bum-bum-tam-tam": 44,
    "i-want-it-that-way": 45,
    "blue": 46,
    "its-not-unusual": 47,  # premium
    "friday": 48,
    "trouble": 49,
    "hit-me-baby": 50,
    "happy": 51,  # premium
    "barbie": 52,
    "bidolibido": 53,
    "bum-bum-tam-tam-2": 54,  # duplicate of 44
    "miami": 55,
    "born-this-way": 56,
    "bad-guy": 57,
    "american-idiot": 58,
    "your-man": 59,
    "despacito": 60,
    "cotton-eye-joe": 61,  # premium
    "my-way": 62,
    "apna-time-aayega": 63,
    "its-raining-men": 64,
    "shake-it-off": 65,
    "chaccaron-maccaron": 66,
    "my-humps": 67,
    "milkshake": 68,  # premium
    "x-gon-give-it-to-ya": 69,
    "rasputin": 70,
    "blinding-lights": 71,
    "in-da-club": 72,  # premium
    "boombastic": 73,  # premium
    "gasolina": 74,
    "axel-f": 75,
    "bites-the-dust": 76,
    "dont-start-now": 77,
    "who-let-the-dogs-out": 78,
    "show-das-poderosas": 79,
    "pepa-no-funk": 80,
    "chaar-botal-vodka": 81,
    "nemashanmah-herati": 82,
    "because-i-got-high": 83,
    "smoke-weed-everyday": 84,
    "mary-jane": 85,
    "three-little-birds": 86,
    "2-joints": 87,
    "-": 88,  # No sound
    "have-you-ever-had-a-dream": 89,
    "heat-waves": 90,
    "tell-me-you-know": 91,
    "u-cant-touch-this": 92,  # premium
    "ko": 93,
    "la-bomba": 94,
    "rowdy-baby": 95,
    "tujhe-dekha-to": 96,
    "watskeburt": 97,
    "drank-and-drugs": 98,
    "zaman": 99,
    "its-the-time-to-disco": 100,
    "heb-je-even-voor-mij": 101,
    "olha-a-explosao": 102,
    "ai-se-eu-te-pego": 103,
    "around-the-world": 104,
    "how-deep-is-your-love": 105,  # premium
    "turn-down-for-what": 106,
    "baby-got-back": 108,  # premium
    "marchas": 110,
    "wayward-son": 112,  # premium
    "drivers-license": 114,
    "get-lucky": 115,
    "gettin-jiggy-wit-it": 116,
    "girls-just-want-to-have-fun": 117,
    "hollaback-girl": 119,
    "kala-chashma": 120,
    "karma-chameleon": 121,  # premium
    "lose-yourself": 122,
    "mamma-mia": 124,  # premium
    "mans-not-hot": 125,
    "new-rules": 127,
    "pump-up-the-jam": 129,
    "run-the-world": 132,
    "sexyback": 133,
    "teen-spirit": 134,
    "tokyo-drift": 135,
    "vai-embrazando": 136,
    "we-are-the-champions": 137,
    "tommy": 139,
    "badtameez-dil": 140,
    "cafe-con-leche": 142,
    "emosanal-attyachaar": 143,
    "kabhi-kabhi-mere-dil-mein": 144,
    "kabhi-kushi-kabhie-gham": 145,
    "kal-ho-naa-ho": 146,
    "queen": 147,
    "m-to-the-b": 150,
    "pyar-hua-iqrar-hua": 150,
    "wiggle": 151,
    "womanizer": 152,
    "kokila-ben": 155,
    "sugarcrash": 156,
    "danza-kuduro": 157,
    "ilarie": 158,
    "mama": 159,
    "motherlover": 160,
    "stacys-mom": 162,
    "stewie-mum": 163,
    "im-a-cool-mom": 164,
    "xtasy": 165,
    "astronaut-in-the-ocean": 166,
    "bad-reputation": 167,
    "dromen-zijn-bedrog": 169,
    "bagagedrager": 170,
    "how-you-like-that": 171,
    "toilet": 172,  # 60fps??
    "pawri-hori-hai": 174,
    "stop-posting-about-among-us": 180,
    "dynamite": 181,
    "dna": 182,
    "its-my-life": 183,
    "scatman": 184,
    "toilet-2": 185,  # duplicate of 172
    "body": 186,
    "oh-no": 187,
    "safety-dance": 193,
    "runaway": 194,
    "mundian-to-bach-ke": 196,
    "money-money-money": 198,
    "gimme-more": 199,
    "california-gurls": 206,
    "fun-song-old": 207,  # 60fps; corrupt thumbnail
    "leave-the-door-open": 211,
    "look-at-me-now": 212,  # premium
    "stressed-out": 218,
    "fun-song": 220,  # 60fps; probably redone to fix the corrupt thumbnail
    "tusa": 245,
}

FIDDLER_DEBUG = True


def main():
    # sys.argv.append(None)
    # sys.argv.append(None)
    # sys.argv.append(None)
    # sys.argv[1] = "freaker.jpg"
    # sys.argv[2] = "170"
    # sys.argv[3] = "freaker.mp4"

    print("Reserving upload location...")
    request_id, s3_fields = step1(TOKEN)

    print("Uploading image...")
    im = Image.open(sys.argv[1])
    rgb_im = im.convert("RGB")
    rgb_im.save("temp.jpg")
    with open("temp.jpg", "rb") as f_image:
        step2(f_image, s3_fields)
    os.remove("temp.jpg")

    print("Beginning processing...")
    step3(TOKEN, request_id, MEMES.get(sys.argv[2], sys.argv[2]))

    video_url = step4(TOKEN, request_id)

    print(f"Downloading finished video to {sys.argv[3]}...")
    step5(sys.argv[3], video_url)


def step1(token: str) -> Tuple[str, S3Fields]:
    """ Reserve an S3 object to upload an image to """
    response = requests.post(
        "https://api.wombo.ai/mobile-app/mashups/",
        headers={
            "authorization": f"Basic {token}",
        },
        verify=not FIDDLER_DEBUG,
    ).json()
    return (response["id"], response["upload_photo"]["fields"])


def step2(f_image: FileIO, s3_fields: dict) -> None:
    """ Upload the image to the S3 location """
    for key in s3_fields:
        s3_fields[key] = (None, s3_fields[key])

    s3_fields["file"] = ("image.jpg", f_image)

    requests.post(
        "https://wombo-user-content.s3.amazonaws.com/",
        files=s3_fields,
        verify=not FIDDLER_DEBUG,
    )


def step3(token: str, request_id: str, meme_id: int) -> None:
    """ Request to begin processing on the uploaded image """
    requests.put(
        f"https://api.wombo.ai/mobile-app/mashups/{request_id}",
        headers={
            "authorization": f"Basic {token}",
        },
        json={
            "meme_id": str(meme_id),
            "premium": False,
        },
        verify=not FIDDLER_DEBUG,
    )


def step4(token: str, request_id: str) -> str:
    """ Poll for completion status """
    while True:
        response = requests.get(
            f"https://api.wombo.ai/mobile-app/mashups/{request_id}",
            headers={
                "authorization": f"Basic {token}",
            },
            verify=not FIDDLER_DEBUG,
        ).json()
        if response["state"] == "completed":
            return response["video_url"]
        elif response["state"] == "failed":
            raise Exception(f"Generation failed: {response}")
        else:
            print(response["state"].capitalize() + "...")
            time.sleep(2)


def step5(output_file_path: str, video_url: str) -> None:
    """ Download completed video """
    video = requests.get(video_url, verify=not FIDDLER_DEBUG).content
    with open(output_file_path, "wb") as f_video:
        f_video.write(video)


if __name__ == "__main__":
    main()
