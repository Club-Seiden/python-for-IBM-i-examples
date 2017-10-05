# Examples using Pillow on IBM i

This example manipulates a [picture](https://commons.wikimedia.org/wiki/File:4-Week-Old_Netherlands_Dwarf_Rabbit.JPG) of an adorable Netherlands Dwarf Rabbit and the IBM i logo using the Python [Pillow](https://python-pillow.org/) library. It demonstrates:

- Resizing the image in half
- Resizing the image to a fixed size
- Resizing the image to fit inside a fixed size, but keeping the aspect ratio the same (thumbnailing)
- Croping the image
- Pasting one image on top of the other (watermarking)

# Installing requisites
 - Make sure you have installed 5733OPS Option 2, along with PTFs SI59051, SI60563, SI60564, and SI61963 (or subsequent PTFs)!
   See [here](https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Python%20PTFs) for the latest PTF numbers.
 - You will need to have GCC installed to compile Pillow. See [here](https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/IBM%20i%20Technology%20Updates/page/Chroot%20Scripts) for info on installing GCC.
 - You will need to have libjpeg installed to build Pillow. This is provided with PTF SI64240.
 - ```MAX_CONCURRENCY=1 CFLAGS=-I/QOpenSys/QIBM/ProdData/OPS/tools/include pip3 install -r requirements.txt```

# Running the Examples
```python3 ./pillow-rabbit.py```

# More Info

- [Pillow documentation](http://pillow.readthedocs.io/en/4.3.x/), specifically the [Image class](http://pillow.readthedocs.io/en/4.3.x/reference/Image.html)