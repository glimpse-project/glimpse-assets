#!/usr/bin/env python3
#
# Copyright (c) 2017 Glimp IP Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# We used to maintain target sequences in terms of a glimpse_target.index
# file that listed filenames for per-frame .json files.
#
# This tool converts a glimpse_target.index + ancillary .json files into a
# single glimpse_target.json. The skeleton for each frame is also a packed
# array of joint [x,y,z] positions - ordered according to a given
# joint-map.json, whereas the previous format had an array of 'bones' with
# 'head' and 'tail' vectors which was a bit more awkward to load while
# glimpse primarily cares just about the joint positions currently.

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('joint_map', help="Path to a joint map")

args = parser.parse_args()

joint_map=None
with open(args.joint_map, 'r') as fp:
    joint_map=json.load(fp);


def find_bone(bones, name, end):

    found = False
    for bone in bones:
        if bone['name'] != name:
            continue

        found = True

        if end in bone:
            point = np.array(bone[end], dtype=np.float32)
            jnt_data.append(point)
        else:
            print("Specified bone end \"%s.%s\" not found in " % (name, end, filename))
            sys.exit(1)
        break
    if found == False:
        print("Failed to find \"%s.%s\" bone in json file %s" % (name, end, filename))
        sys.exit(1)


in_frames = []
with open('glimpse_target.index', 'r') as index_fp:
    index_lines = index_fp.readlines()

    with open('glimpse_target.json', 'w') as out_fp:
        targets = {}
        targets['frames'] = []

        for frame_filename in index_lines:
            with open(frame_filename.strip(), 'r') as in_frame_fp:
                in_frame = json.load(in_frame_fp)
                out_frame = {}

                out_joints = []

                bones = in_frame['bones']

                for joint in joint_map:
                    split_name = joint['joint'].split('.')

                    if len(split_name) != 2:
                        print("Bad bone name \"" + joint['joint'] + "\", expected " +
                              "name to be in the form: bone_name.head or bone_name.tail");
                        sys.exit(1)

                    name = split_name[0]
                    end = split_name[1]

                    for bone in bones:
                        if bone['name'] == name:
                            out_joint = {
                                'x': bone[end][0],
                                'y': bone[end][1],
                                'z': bone[end][2]
                            }
                            out_joints.append(out_joint)
                            break

                out_frame['joints'] = out_joints
                targets['frames'].append(out_frame)

        json.dump(targets, out_fp, indent=4)

