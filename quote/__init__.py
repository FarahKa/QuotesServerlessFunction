import logging
from PIL import Image, ImageDraw, ImageFont
import azure.functions as func
import requests
import json
import io
import textwrap


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    #je récupère la template souhaitée
    try:
        req_body = req.get_json()
        template = req_body.get("template")
        logging.info('Template: '+template)
    except ValueError:
        pass
    #je récupère la citation souhaitée
    try:
        req_body = req.get_json()
        citation = req_body.get("citation")
        logging.info('Citation: '+citation)
    except ValueError:
        pass
    #je récupère une image
    if not template or not citation:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a template and a citation in the request body for a personalized response.",
             status_code=200
        )

    r = requests.get("https://api.pexels.com/v1/search?query="+template+"&per_page=1", headers={"Authorization": "563492ad6f9170000100000171c9a33e5a964c9286b39afd68d4ee2c"})
    result = r.json()["photos"][0]["src"]["medium"]
    response = requests.get(result, headers={"Authorization": "563492ad6f9170000100000171c9a33e5a964c9286b39afd68d4ee2c"})
    logging.info('url: '+result)
    desc_fnt = ImageFont.truetype("quote/DejaVuSerif-Bold.ttf", 20)
    with Image.open(io.BytesIO(response.content)).convert("RGBA") as base:
        # make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", base.size, (255,255,255,0))
        # get a drawing context
        d = ImageDraw.Draw(txt)
        # draw text
        offset = 20
        interligne = 3
        for line in textwrap.wrap(citation, width=20):
            d.text((10+2, offset+2), line, font=desc_fnt, fill=(255,255,255))
            d.text((10, offset), line, font=desc_fnt, fill=(0,0,0))
            offset += desc_fnt.getsize(line)[1] + interligne
        out = Image.alpha_composite(base, txt)
        img_byte_arr = io.BytesIO()
        out.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

    return func.HttpResponse(img_byte_arr, status_code=200, mimetype="image/png")


