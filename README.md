# vgg-faces-loader
Script to download and annotate images from VGG Faces dataset


### Usage


Download VGG Face Dataset from it's home page:

http://www.robots.ox.ac.uk/~vgg/data/vgg_face/

Or:

https://mega.nz/#!zeQSwC7D!aOBgSYkvldL6k91VdwKIx_EKS1J3_MQduPEU3QQ8g-o

You would get a file `vgg_face_dataset.tar.gz` that contains a `vgg_face_dataset` folder.



```
git clone https://github.com/ndaidong/vgg-faces-loader.git
cd vgg-faces-loader

tar -zxvf vgg_face_dataset.tar.gz

python3 -m venv venv
source venv/bin/activate

(venv) pip install -r requirements
(venv) ./script.py -d vgg_face_dataset/files -o output
```

The process may take several days depending on the connectivity.
It would try to download about 2.6 milions images from many resources.
However, we just expect to get about 1 milion.
Almost of links no longer available for right now.

![Downloading](https://i.imgur.com/w5Q6bF8.png)


### labelImg


To check and modify the labels after downloading finishes.


```
(venv) labelImg
```

Specify image dir and label dir to get:

![labelImg](https://i.imgur.com/IZH6t72.png)


### Dataset

http://www.robots.ox.ac.uk/~vgg/data/vgg_face/
