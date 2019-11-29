#!/usr/bin/env python3

import os
import numpy
import random
import string
import cv2
import argparse
import captcha.image
import subprocess
import shutil

def scramble(captcha_text, user_id, salt, project_number):
    import hashlib
    m = hashlib.sha1()
    plaintext = user_id + salt + project_number + captcha_text
    m.update(plaintext.encode('utf-8'))
    return m.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--width', help='Width of captcha image', type=int)
    parser.add_argument('--height', help='Height of captcha image', type=int)
    parser.add_argument('--length', help='Length of captchas in characters', type=int)
    parser.add_argument('--count', help='How many captchas to generate', type=int)
    parser.add_argument('--symbols', help='File with the symbols to use in captchas', type=str)
    parser.add_argument('--output-dir', help='Where to store the generated challenges', type=str)
    parser.add_argument('--user-id', help='', type=str)
    parser.add_argument('--salt', help='', type=str)
    parser.add_argument('--project-number', help='', type=str)
    args = parser.parse_args()

    if args.width is None:
        print("Please specify the captcha image width")
        exit(1)

    if args.height is None:
        print("Please specify the captcha image height")
        exit(1)

    if args.length is None:
        print("Please specify the captcha length")
        exit(1)

    if args.count is None:
        print("Please specify the captcha count to generate")
        exit(1)

    if args.output_dir is None:
        print("Please specify the output directory")
        exit(1)

    if args.symbols is None:
        print("Please specify the captcha symbols file")
        exit(1)

    if args.user_id is None:
        print("Please specify the userid")
        exit(1)

    if args.salt is None:
        print("Please specify the salt string file")
        exit(1)

    if args.project_number is None:
        print("Please specify the project number")
        exit(1)

    captcha_generator = captcha.image.ImageCaptcha(width=args.width, height=args.height)

    symbols_file = open(args.symbols, 'r')
    captcha_symbols = symbols_file.readline().strip()
    symbols_file.close()

    if not os.path.exists(args.output_dir):
        print("Creating output directory " + args.output_dir)
        os.makedirs(args.output_dir)

    challenge_data_directory = os.path.join(args.output_dir, args.user_id, 'challenge')
    if not os.path.exists(challenge_data_directory):
        os.makedirs(challenge_data_directory)

    challenge_submitty_csv = os.path.join(args.output_dir, args.user_id, 'submitty-'+args.user_id+'.csv')

    mapping = dict()

    with open(challenge_submitty_csv, 'w') as submitty_file:
        print("Generating " + str(args.count) + " captchas with symbol set {" + captcha_symbols + "}")
        for i in range(args.count):
            captcha_text = ''.join([random.choice(captcha_symbols) for j in range(args.length)])
            image_name_scrambled = scramble(captcha_text, args.user_id, args.salt, args.project_number)
            image_path = os.path.join(args.output_dir, args.user_id, 'challenge', image_name_scrambled + '.png')

            if os.path.exists(image_path):
                while os.path.exists(image_path): # try a different captcha
                    captcha_text = ''.join([random.choice(captcha_symbols) for j in range(args.length)])
                    image_name_scrambled = scramble(captcha_text, args.user_id, args.salt, args.project_number)
                    image_path = os.path.join(args.output_dir, args.user_id, 'challenge', image_name_scrambled + '.png')

            image = numpy.array(captcha_generator.generate_image(captcha_text))

            cv2.imwrite(image_path, image)
            mapping[image_name_scrambled+'.png'] = captcha_text

        print("Saving submission CSV file for " + args.user_id + ": " + challenge_submitty_csv)
        for filename in sorted(mapping.keys()):
            submitty_file.write(filename + "," + mapping[filename] + "\n")

        print("Creating challenge zip file: " + os.path.join(args.output_dir, args.user_id, 'challenge.zip'))
        subprocess.call(['zip', '-r', '-j',
                                os.path.join(args.output_dir, args.user_id, 'challenge.zip'),
                                os.path.join(args.output_dir, args.user_id, 'challenge')],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        shutil.rmtree(os.path.join(args.output_dir, args.user_id, 'challenge'))

if __name__ == '__main__':
    main()
