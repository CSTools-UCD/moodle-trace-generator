from dominate.tags import img
from builder.extra_tags import embeddedfile
from typing import Tuple
import base64

def get_image(image_name : str)-> Tuple[img, embeddedfile]:
  image_file_name = image_name.split("/")[-1].split(".")[0]
  image_file  = open(image_name, "rb")
  image = base64.b64encode(image_file.read())
  image_tag = img(src="@@PLUGINFILE@@/"+image_file_name, alt="" ,width="100%", style="object-fit:contain", role="presentation", cls="img-responsive atto_image_button_text-bottom")
  encoded_image = embeddedfile(str(image)[2:-1], name=image_file_name, path="/", encoding="base64")
  return (image_tag, encoded_image)