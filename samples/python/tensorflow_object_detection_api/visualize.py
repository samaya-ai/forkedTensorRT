#
# SPDX-FileCopyrightText: Copyright (c) 1993-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np
np.set_printoptions(threshold=np.inf, suppress=True)

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont



COLORS = ['GoldenRod', 'MediumTurquoise', 'GreenYellow', 'SteelBlue', 'DarkSeaGreen', 'SeaShell', 'LightGrey',
          'IndianRed', 'DarkKhaki', 'LawnGreen', 'WhiteSmoke', 'Peru', 'LightCoral', 'FireBrick', 'OldLace',
          'LightBlue', 'SlateGray', 'OliveDrab', 'NavajoWhite', 'PaleVioletRed', 'SpringGreen', 'AliceBlue', 'Violet',
          'DeepSkyBlue', 'Red', 'MediumVioletRed', 'PaleTurquoise', 'Tomato', 'Azure', 'Yellow', 'Cornsilk',
          'Aquamarine', 'CadetBlue', 'CornflowerBlue', 'DodgerBlue', 'Olive', 'Orchid', 'LemonChiffon', 'Sienna',
          'OrangeRed', 'Orange', 'DarkSalmon', 'Magenta', 'Wheat', 'Lime', 'GhostWhite', 'SlateBlue', 'Aqua',
          'MediumAquaMarine', 'LightSlateGrey', 'MediumSeaGreen', 'SandyBrown', 'YellowGreen', 'Plum', 'FloralWhite',
          'LightPink', 'Thistle', 'DarkViolet', 'Pink', 'Crimson', 'Chocolate', 'DarkGrey', 'Ivory', 'PaleGreen',
          'DarkGoldenRod', 'LavenderBlush', 'SlateGrey', 'DeepPink', 'Gold', 'Cyan', 'LightSteelBlue', 'MediumPurple',
          'ForestGreen', 'DarkOrange', 'Tan', 'Salmon', 'PaleGoldenRod', 'LightGreen', 'LightSlateGray', 'HoneyDew',
          'Fuchsia', 'LightSeaGreen', 'DarkOrchid', 'Green', 'Chartreuse', 'LimeGreen', 'AntiqueWhite', 'Beige',
          'Gainsboro', 'Bisque', 'SaddleBrown', 'Silver', 'Lavender', 'Teal', 'LightCyan', 'PapayaWhip', 'Purple',
          'Coral', 'BurlyWood', 'LightGray', 'Snow', 'MistyRose', 'PowderBlue', 'DarkCyan', 'White', 'Turquoise',
          'MediumSlateBlue', 'PeachPuff', 'Moccasin', 'LightSalmon', 'SkyBlue', 'Khaki', 'MediumSpringGreen',
          'BlueViolet', 'MintCream', 'Linen', 'SeaGreen', 'HotPink', 'LightYellow', 'BlanchedAlmond', 'RoyalBlue',
          'RosyBrown', 'MediumOrchid', 'DarkTurquoise', 'LightGoldenRodYellow', 'LightSkyBlue']


#Overlay mask with transparency on top of the image.
def overlay(image, mask, color, alpha_transparency=0.5):
    for channel in range(3):
        image[:, :, channel] = np.where(mask == 1,
                              image[:, :, channel] *
                              (1 - alpha_transparency) + alpha_transparency * color[channel] * 255,
                              image[:, :, channel])
    return image

def visualize_detections(image_path, output_path, detections, labels=[]):
    image = Image.open(image_path).convert(mode='RGB')
    # Get image dimensions.
    im_width, im_height = image.size
    line_width = 2
    font = ImageFont.load_default()
    for d in detections:
        color = COLORS[d['class'] % len(COLORS)]
        # Dynamically convert PIL color into RGB numpy array.
        pixel_color = Image.new("RGB",(1, 1), color)
        # Normalize.
        np_color = (np.asarray(pixel_color)[0][0])/255
        # Process TF and TRT instance segmentation masks.
        if isinstance(d['mask'], np.ndarray) and d['mask'].shape == (33, 33):
            # Get detection bbox resolution.
            det_width = round(d['xmax'] - d['xmin'])
            det_height = round(d['ymax'] - d['ymin'])
            # Create an image out of predicted mask array.
            small_mask = Image.fromarray(d['mask'])
            # Upsample mask to detection bbox's size.
            mask = small_mask.resize((det_width, det_height), resample=Image.BILINEAR)
            # Create an original image sized template for correct mask placement.
            pad = Image.new("L", (im_width, im_height))
            # Place your mask according to detection bbox placement.
            pad.paste(mask, (round(d['xmin']), (round(d['ymin']))))
            # Reconvert mask into numpy array for evaluation.
            padded_mask = np.array(pad)
            #Creat np.array from original image, copy in order to modify.
            image_copy = np.asarray(image).copy()
            # Image with overlaid mask.
            masked_image = overlay(image_copy, padded_mask, np_color)
            # Reconvert back to PIL.
            image = Image.fromarray(masked_image)
        # Separate clause for ground truth instance segmentation masks.
        elif isinstance(d['mask'], np.ndarray):
            #Creat np.array from original image, copy in order to modify.
            image_copy = np.asarray(image).copy()
            # Image with overlaid mask.
            masked_image = overlay(image_copy, d['mask'], np_color)
            # Reconvert back to PIL
            image = Image.fromarray(masked_image)

        # Bbox lines.
        draw = ImageDraw.Draw(image)
        draw.line([(d['xmin'], d['ymin']), (d['xmin'], d['ymax']), (d['xmax'], d['ymax']), (d['xmax'], d['ymin']),
                   (d['xmin'], d['ymin'])], width=line_width, fill=color)
        label = "Class {}".format(d['class'])
        if d['class'] < len(labels):
            label = "{}".format(labels[d['class']])
        score = d['score']
        text = "{}: {}%".format(label, int(100 * score))
        if score < 0:
            text = label
        text_width, text_height = font.getsize(text)
        text_bottom = max(text_height, d['ymin'])
        text_left = d['xmin']
        margin = np.ceil(0.05 * text_height)
        draw.rectangle([(text_left, text_bottom - text_height - 2 * margin), (text_left + text_width, text_bottom)],
                       fill=color)
        draw.text((text_left + margin, text_bottom - text_height - margin), text, fill='black', font=font)
    if output_path is None:
        return image
    image.save(output_path)


def concat_visualizations(images, names, colors, output_path):
    def draw_text(draw, font, text, width, bar_height, offset, color):
        text_width, text_height = font.getsize(text)
        draw.rectangle([(offset, 0), (offset + width, bar_height)], fill=color)
        draw.text((offset + (width - text_width) / 2, text_height - text_height / 2), text, fill='black', font=font)

    bar_height = 18
    width = 0
    height = 0
    for im in images:
        width += im.width
        height = max(height, im.height)

    concat = Image.new('RGB', (width, height + bar_height))
    draw = ImageDraw.Draw(concat)
    font = ImageFont.load_default()

    offset = 0
    for i, im in enumerate(images):
        concat.paste(im, (offset, bar_height))
        draw_text(draw, font, names[i], im.width, bar_height, offset, colors[i])
        offset += im.width

    if output_path is None:
        return concat
    concat.save(output_path)