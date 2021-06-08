from io import FileIO
from typing import Tuple
from typing import TypedDict

import requests
import time


class S3Fields(TypedDict):
    key: str
    AWSAccessKeyId: str
    policy: str
    signature: str


# I'm not sure if this token is unique to my phone or the one request I
# reverse-engineered this from, but I do know that you can reuse them, so this
# can just stay hard-coded
TOKEN = "d29tYm8tdGhhdC1zaGl6ejpHZXRUaGF0QnJlYWQkMSE="


def main():
    print("Reserving upload location...")
    request_id, s3_fields = step1(TOKEN)

    print("Uploading image...")
    with open("freaker.jpg", "rb") as f_image:
        step2(f_image, s3_fields)

    for meme_id in range(-1, 1):
        print(f"Testing meme ID {meme_id}... ", end="")
        step3(TOKEN, request_id, meme_id)

        try:
            video_url = step4(TOKEN, request_id)
        except:
            print("❌")
        else:
            step5(f"tests/test-{meme_id}.mp4", video_url)


def step1(token: str) -> Tuple[str, S3Fields]:
    """ Reserve an S3 object to upload an image to """
    response = requests.post(
        "https://api.wombo.ai/mobile-app/mashups/",
        headers={
            "authorization": f"Basic {token}",
        },
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
        }
    )


def step4(token: str, request_id: str) -> str:
    """ Poll for completion status """
    reported_status = False
    while True:
        response = requests.get(
            f"https://api.wombo.ai/mobile-app/mashups/{request_id}",
            headers={
                "authorization": f"Basic {token}",
            }
        ).json()
        if response["state"] == "completed":
            return response["video_url"]
        elif response["state"] == "failed":
            raise Exception(f"Generation failed: {response}")
        else:
            if not reported_status and response["state"] != "pending":
                print("✅")
                reported_status = True
            time.sleep(2)


def step5(output_file_path: str, video_url: str) -> None:
    """ Download completed video """
    video = requests.get(video_url).content
    with open(output_file_path, "wb") as f_video:
        f_video.write(video)


if __name__ == "__main__":
    main()
