def detect_text_uri(uri):

    from google.cloud import vision # Куда ты импорт засунула?)))
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    for text in texts:
        name_comic = text.description
        print(name_comic)
        return name_comic
