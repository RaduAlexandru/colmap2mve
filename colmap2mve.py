from collections import namedtuple
import os
import sys, getopt
import Image
from shutil import copyfile
import numpy as np
import nibabel as nib
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0



def read_cameras_txt(file_path):
    # file_path="/media/alex/Data/Master/SHK/sfm/Data/Colmap/blub/cameras.txt"
    print "read_cameras: file is", file_path

    camera = namedtuple('camera', ['cam_id', 'model', 'width', 'height', 'focal_length', 'p_x', 'p_y', 'd_0'])
    camera_list = []

    with open(file_path, "r") as f:
        for line in f:
            li=line.strip()
            if not li.startswith("#"):
                line=line.rstrip()

                line= line.split(" ")

                cam = camera (cam_id=line[0],
                              model=line[1],
                              width=line[2],
                              height=line[3],
                              focal_length=line[4],
                              p_x=line[5],
                              p_y=line[6],
                              d_0=line[7])
                camera_list.append(cam)
                # print (cam)

    return camera_list


def read_images_txt(file_path):
    print "read_images_txt: file is", file_path

    # file_path="/media/alex/Data/Master/SHK/sfm/Data/Colmap/blub/images.txt"

    image = namedtuple('image', ['img_id', 'qw', 'qx', 'qy', 'qz', 'tx', 'ty', 'tz', 'cam_id', 'name', 'points2D_list'])
    point2D = namedtuple('point2D', ['x', 'y', 'point3D_id'])

    image_list=[]

    # IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME

    first_line=True

    with open(file_path, "r") as f:
        for line in f:
            li=line.strip()
            if not li.startswith("#"):
                line=line.rstrip()

                line= line.split(" ")

                #if its the first line we read info about the orientation, for the second we read the keypoints
                if (first_line):

                    #HACK fix for img_id to be 0 based index
                    line[0]=str(int(line[0])-39)
                    print line[0]

                    img = image (img_id=line[0],
                                 qw=line[1],
                                 qx=line[2],
                                 qy=line[3],
                                 qz=line[4],
                                 tx=line[5],
                                 ty=line[6],
                                 tz=line[7],
                                 cam_id=line[8],
                                 name=line[9],
                                 points2D_list=[])





                    image_list.append(img)
                    first_line=False;
                else:
                    img=image_list[-1]
                    points2D_list=[]

                    #go throught the line and every 3 values add a point
                    for i in range(0, len(line)/3):
                        p=point2D(x=line[i*3],
                                  y=line[1 + i*3],
                                  point3D_id=line[2 + i*3])
                        img.points2D_list.append(p)

                    first_line=True

    return image_list

def read_points3D_txt(file_path):
    print "read_points3D_txt: file is", file_path

    # file_path="/media/alex/Data/Master/SHK/sfm/Data/Colmap/blub/points3D.txt"


    # POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)

    point3D = namedtuple('point3D', ['point3D_id','x', 'y', 'z', 'r', 'g', 'b', 'error', 'track'])
    track = namedtuple('track', ['img_id', 'point2D_id'])

    points3D_list=[]


    with open(file_path, "r") as f:
        for line in f:
            li=line.strip()
            if not li.startswith("#"):
                line=line.rstrip()

                line= line.split(" ")

                p = point3D  (point3D_id=line[0],
                              x=line[1],
                              y=line[2],
                              z=line[3],
                              r=line[4],
                              g=line[5],
                              b=line[6],
                              error=line[7],
                              track=[])

                #TODO read the rest of the line and put it into track
                length=len(line)-8
                for i in range (0,length/2):

                    #HACK fix for img_id to be 0 based index
                    line[i*2 + 8]=str(int(line[i*2 + 8])-39)

                    tr=track(img_id=line[i*2 + 8],
                             point2D_id=line[1 + i*2 + 8])

                    p.track.append(tr)

                points3D_list.append(p)

    return points3D_list


def create_scene(input,output,camera_list,imgs_list,points3D_list):
    print "create_scene: input is", input
    print "create_scene: output is", output
    print 'creating scene'

    #creating views
    create_views(os.path.normpath(input+ "/images/"),os.path.normpath(output+"/views"),camera_list,imgs_list)


    #create synth_0.out
    create_synth(os.path.normpath(output),camera_list, imgs_list, points3D_list)


def create_views(input,output,camera_list,imgs_list):
    print "create_views: input is", input
    print "create_views: output is", output
    #create the views folder

    # for each img in the imgs_list
        # create teh views_000 folder
        #get the png image asociatd.
        #copy it in the folder
        #resize it to a smaller one and copy it also inside the folder

        #transform the rotation from quaterion to roatation matrix

        #put all the data into meta.ini



    if not os.path.exists(output):
        os.makedirs(output)

    for img_info in imgs_list:
        print img_info.img_id, "  ", img_info.name

        #make the .mve subdirectory
        num="%04d" % (int (img_info.img_id),)
        save_path=os.path.normpath(output + "/view_" +num + ".mve" )
        if not os.path.exists(save_path):
            os.makedirs(save_path)


        img_path=os.path.normpath(input + "/" + img_info.name)
        copyfile(img_path, os.path.normpath(save_path + "/undistored.png"))

        # # thumbnail
        im = Image.open(img_path)
        size= 50,50
        # im.thumbnail(size, Image.ANTIALIAS)
        im.thumbnail(size, Image.NEAREST)
        im.save(os.path.normpath(save_path + "/thumbnail.png"), "png")

        #meta.ini

        #focal length
        #read from the cam id. with that id, use the cam_id_vec and find the cam. grab the focal lengh
        #TODO actually loop through every camera but for now just grabbing the only one should suffice
        cam_idx=0
        cam=camera_list[cam_idx]
        larger_side=max(float(cam.width), float(cam.height))
        focal_length=float(cam.focal_length)/larger_side

        #principal point
        p_x=float(cam.p_x)/float(cam.width)
        p_y=float(cam.p_y)/float(cam.height)


        #rotation
        q = [float(img_info.qw), float(img_info.qx), float(img_info.qy), float(img_info.qz)]
        rot = nib.quaternions.quat2mat(q)
        rot_str = ' '.join(str(x) for x in  np.nditer(rot))




        #create and write
        config = ConfigParser()
        config.add_section('camera')
        config.set('camera', 'focal_length', focal_length)
        config.set('camera', 'pixel_aspect', 1)
        config.set('camera', 'principal_point', str(p_x) + " " + str(p_y))
        config.set('camera', 'rotation', rot_str)
        config.set('camera', 'translation', str(img_info.tx) + " " +  str(img_info.ty) + " " + str(img_info.tz))
        config.add_section('view')
        config.set('view', 'id', img_info.img_id)
        config.set('view', 'name', num)
        with open(os.path.normpath(save_path + "/meta.ini"), 'w') as configfile:
            config.write(configfile)


        # for x in np.nditer(rot):
        #     print x


def create_synth(output,camera_list, imgs_list, points3D_list):
    print "creating synth"

    f = open(os.path.normpath(output + '/synth_0.out'), 'w+')

    f.write('drews 1.0\n') # python will convert \n to os.linesep
    f.write(str(len(imgs_list)) + " " + str(len(points3D_list)) + "\n" )

    for img_info in imgs_list:
        #TODO get the corespodin camera by the index from img_info
        cam_idx=0
        cam=camera_list[cam_idx]

        q = [float(img_info.qw), float(img_info.qx), float(img_info.qy), float(img_info.qz)]
        rot = nib.quaternions.quat2mat(q)
        rot_str = ''.join(str(x) for x in  np.nditer(rot))


        larger_side=max(float(cam.width), float(cam.height))
        focal_length=float(cam.focal_length)/larger_side

        rot_str=rot.tolist()

        val=rot[0][2]


        #TODO fix rotation writing
        f.write(str(focal_length) + " " + str(cam.d_0) + " " +  str(0) +  "\n")
        # f.write(str(rot_str[0]) + " " + str(rot_str[1]) + " " + str(rot_str[2]) + "\n" )
        # f.write(rot_str[3] + " " +rot_str[4] + " " +rot_str[5] + "\n" )
        # f.write(rot_str[6] + " " +rot_str[7] + " " +rot_str[8] + "\n" )
        # f.write(str(rot_str[0])[1:-1] + "\n")
        # f.write(str(rot_str[1])[1:-1] + "\n")
        # f.write(str(rot_str[2])[1:-1] + "\n")
        f.write(str(rot[0][0]) + " " + str(rot[0][1]) + " " + str(rot[0][2]) + "\n" )
        f.write(str(rot[1][0]) + " " + str(rot[1][1]) + " " + str(rot[1][2]) + "\n" )
        f.write(str(rot[2][0]) + " " + str(rot[2][1]) + " " + str(rot[2][2]) + "\n" )
        f.write(img_info.tx + " " +img_info.ty + " " +img_info.tz + "\n" )


    for point in points3D_list:
        f.write(point.x + " " + point.y + " " +point.z + "\n" )
        f.write(point.r + " " + point.g + " " +point.b + "\n" )
        f.write(str(len(point.track)) + " " )

        for tr in point.track:
            f.write(str(tr.img_id) + " " +  str(tr.point2D_id) + " " +  str(0) + " ")
        f.write("\n")
    f.close() # you can omit in most cases as the destructor will call it

def main(argv):



    input = ''
    output = ''
    try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print 'colmap2mve.py -i <input> -o <output>'
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print 'colmap2mve.py -i <input> -o <output>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         input = arg
      elif opt in ("-o", "--ofile"):
         output = arg
    if (len(sys.argv)!=5  ):
         print 'colmap2mve.py -i <input> -o <output>'
         sys.exit(2)

    print 'Input file is "', input
    print 'Output file is "', output


    print "starting importing"

    #read camera.txt
    camera_list = read_cameras_txt(os.path.normpath(input+"/blub/cameras.txt"))
    print camera_list




    #read images.txt
    imgs_list= read_images_txt(os.path.normpath(input+"/blub/images.txt"))
    # print imgs_list[0]

    #read points3D.txt
    points3D_list=read_points3D_txt(os.path.normpath(input+"/blub/points3D.txt"))
    print points3D_list[0:2]

    create_scene(os.path.normpath(input),os.path.normpath(output),camera_list,imgs_list,points3D_list)



    print "finished"

if __name__ == "__main__":
    main(sys.argv[1:])
