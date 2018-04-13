#!/usr/bin/env python3

import glob
import argparse
import csv
import re

import xml.etree.cElementTree as ET

from xml.dom import minidom
from urllib import request
from os import path, mkdir
from shutil import rmtree, copy
from collections import namedtuple
from time import time, ctime
from datetime import timedelta
from random import shuffle

from PIL import Image

Link = namedtuple('Link', [
    'id',
    'url',
    'left',
    'top',
    'right',
    'bottom',
    'pose',
    'detection_score',
    'curation',
    'realname',
    'alias',
])


regex = re.compile('[^a-zA-Z0_9]')


def make_alias(txt=''):
    return regex.sub('_', txt.lower())


def normalize(val):
    v = int(val)
    return str(v)


def build_annotation(link, fpath, output):
    img_fname = link.alias + '_' + link.id + '.jpg'
    lab_fname = link.alias + '_' + link.id + '.xml'

    img_fpath = 'images/' + img_fname
    lab_fpath = 'labels/' + lab_fname

    print('Generating annotation file: "{}"'.format(lab_fpath))

    root = ET.Element('annotation')
    ET.SubElement(root, 'folder').text = 'images'
    ET.SubElement(root, 'filename').text = img_fname
    ET.SubElement(root, 'path').text = img_fpath

    source = ET.SubElement(root, 'source')
    ET.SubElement(source, 'database').text = 'vgg_faces_dataset'

    im = Image.open(fpath)
    width = im.width
    height = im.height

    size = ET.SubElement(root, 'size')
    ET.SubElement(size, 'width').text = normalize(width)
    ET.SubElement(size, 'height').text = normalize(height)
    ET.SubElement(size, 'depth').text = '3'

    ET.SubElement(root, 'segmented').text = '0'

    ob = ET.SubElement(root, 'object')
    ET.SubElement(ob, 'name').text = 'face'
    ET.SubElement(ob, 'pose').text = link.pose
    ET.SubElement(ob, 'truncated').text = '0'
    ET.SubElement(ob, 'difficult').text = '0'
    ET.SubElement(ob, 'realname').text = link.realname

    left = float(link.left)
    top = float(link.top)
    right = float(link.right)
    bottom = float(link.bottom)

    box = ET.SubElement(ob, 'bndbox')
    ET.SubElement(box, 'xmin').text = normalize(left)
    ET.SubElement(box, 'ymin').text = normalize(top)
    ET.SubElement(box, 'xmax').text = normalize(right)
    ET.SubElement(box, 'ymax').text = normalize(bottom)

    xml_string = ET.tostring(root)
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent='  ')
    with open(output + '/' + lab_fpath, 'wb') as f:
        f.write(pretty_xml.encode('utf-8'))
    print('Generated annotation file: "{}"'.format(lab_fpath))
    return root


def savefile(content, link, output):
    fname = link.alias + '_' + link.id + '.jpg'
    f = output + '/images/' + fname
    try:
        print('Saving image: "{}"'.format(f))
        o = open(f, 'wb')
        o.write(content)
        o.close()
        print('Saved image: "{}"'.format(f))
        build_annotation(link, f, output)
    except Exception as err:
        print('Error while saving image "{}"'.format(f))
        print('URL: "{}"'.format(link.url))
        print(err)


def retrieve(entries=[], output='./'):
    current = 0
    success = 0
    failed = 0
    total = len(entries)
    start_time = int(time())
    print('Total entries: {}'.format(total))
    for entry in entries:
        current += 1
        url = entry.url
        print('Retrieving data from "{}"...'.format(url))
        try:
            res = request.urlopen(url, None, 15)
            status = res.getcode()
            info = res.info()
            content_type = info['content-type']
            if status != 200:
                print('Link is not available: "{}"'.format(url))
                failed += 1
            elif not content_type.startswith('image/jp'):
                print('Resource is not image: "{}"'.format(url))
                failed += 1
            else:
                print('Handling item {}/{}'.format(current, total))
                total_case = success + failed
                success_rate = normalize(success * 100 / total_case)
                failed_rate = normalize(failed * 100 / total_case)
                current_time = int(time())
                strtime = ctime(current_time)
                duration = current_time - start_time
                print('Since: {}, now: {}'.format(ctime(start_time), strtime))
                print('Duration: {}'.format(timedelta(seconds=duration)))
                print('Success: {} (~{}%)'.format(success, success_rate))
                print('Failed: {} (~{}%)'.format(failed, failed_rate))
                savefile(res.read(), entry, output)
                success += 1
        except Exception as err:
            failed += 1
            print('Error while downloading image "{}"'.format(url))
            print(err)


def process(files, output):
    print('Total files: {}'.format(len(files)))
    links = []
    print('Extracting links from files...')
    for filename in files:
        name_file = path.basename(filename)
        realname = name_file.replace('.txt', '').replace('_', ' ')
        alias = make_alias(realname)
        ifile = open(filename, 'r')
        reader = csv.reader(ifile, delimiter=' ')
        for row in reader:
            entry = Link(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                realname,
                alias,
            )
            links.append(entry)
    shuffle(links)
    return retrieve(links, output)


def load(d, o):
    files = glob.glob(d + '/*.txt')
    if path.exists(o):
        rmtree(o)
    mkdir(o)
    mkdir(o + '/images')
    mkdir(o + '/labels')
    return process(files, o)


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dir',
        help='Path to source dir'
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Path to output dir'
    )
    args = parser.parse_args()
    if not args.dir:
        print('Please specify path to source dir')
    elif not args.output:
        print('Please specify path to output')
    else:
        entries = load(
            path.normpath(args.dir),
            path.normpath(args.output)
        )


if __name__ == '__main__':
    start()
