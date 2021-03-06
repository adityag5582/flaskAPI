import numpy as np
import cv2
import json
from flask import Flask,request,Response,jsonify
import os
from matplotlib import pyplot as plt
from PIL import Image
import shutil
# from transform_example import transfer
#from pyimagesearch.transform import four_point_transform
# from connected_component import components
# from image_regg import registration
#from coords import box_extractionqw

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def hello():
    return "hello"


@app.route('/upload',methods=['GET','POST'])
def upload():
    dirname="SAVED"
    os.mkdir(dirname)
    images=request.files.to_dict()
    j=0;
    for image in images:
        print(images[image])
        file_name = images[image].filename
        images[image].save("SAVED/"+str(j)+".jpg")
        j=j+1
    # print(j)
    dirname = "RUN"
    os.mkdir(dirname)

    dirname = "RUN/Cropped"
    os.mkdir(dirname)

    dirname="RUN/Cropped/OMR"
    os.mkdir(dirname)
    dirname="RUN/Cropped/ANSWER_KEY"
    os.mkdir(dirname)

    dirname="RUN/Registered"
    os.mkdir(dirname)
    dirname="RUN/Difference"
    os.mkdir(dirname)


    for j in range(1,2):
        dirname=("RUN/Cropped/ROLLNO_"+str(j))
        os.mkdir(dirname)

        dirname=("RUN/Registered/ROLLNO_"+str(j))
        os.mkdir(dirname)
        dirname="RUN/Registered/ROLLNO_"+ str(j) +"/Filled"
        os.mkdir(dirname)
        dirname="RUN/Registered/ROLLNO_"+ str(j) +"/Empty"
        os.mkdir(dirname)

        dirname=("RUN/Difference/ROLLNO_"+str(j))
        os.mkdir(dirname)
        dirname="RUN/Difference/ROLLNO_"+ str(j) +"/Filled"
        os.mkdir(dirname)
        dirname="RUN/Difference/ROLLNO_" + str(j) + "/Empty"
        os.mkdir(dirname)
    box_extraction("SAVED/0.jpg","./RUN/Cropped/OMR/")
    box_extraction("SAVED/2.jpg","./RUN/Cropped/ANSWER_KEY/")
    box_extraction("SAVED/1.jpg","./RUN/Cropped/ROLLNO_"+str(1)+"/")
    registration()
    list=components()
    # print(list)
    cattempted=list[0]
    cunattempt=list[1]
    wrong=list[2]
    score=list[3]
    # print(int(cattempted))
    # print(int(cunattempt))
    # print(int(wrong))
    # print(int(score))
    # shutil.rmtree('RUN/Difference/ROLLNO_1/Empty')
    # shutil.rmtree('RUN/Difference/ROLLNO_1/Filled')
    # shutil.rmtree('RUN/Difference/ROLLNO_1')
    shutil.rmtree('RUN/Difference')
    # shutil.rmtree('RUN/Registered/ROLLNO_1/Empty')
    # shutil.rmtree('RUN/Registered/ROLLNO_1/Filled')
    # shutil.rmtree('RUN/Registered/ROLLNO_1')
    shutil.rmtree('RUN/Registered')
    # shutil.rmtree('RUN/Cropped/ROLLNO_1')
    # shutil.rmtree('RUN/Cropped/ANSWER_KEY')
    # shutil.rmtree('RUN/Cropped/OMR')
    shutil.rmtree('RUN/Cropped')
    shutil.rmtree('RUN')
    shutil.rmtree('SAVED')
    # os.remove('0.jpg')
    # os.remove('1.jpg')
    # os.remove('2.jpg')
    return jsonify(attempted=str(int(cattempted)),unattemped=str(int(cunattempt)),wrong=str(int(wrong)),score=str(score))

def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0

    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1

    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)

def box_extraction(img_for_box_extraction_path, cropped_dir_path):

    img = cv2.imread(img_for_box_extraction_path, 0)  # Read the image
    img2 = cv2.imread(img_for_box_extraction_path, 0)
    img3 = cv2.imread(img_for_box_extraction_path, 0)
    font = cv2.FONT_HERSHEY_COMPLEX
    # img = cv2.blur(img,(10,10))
    (thresh, img_bin) = cv2.threshold(img, 128, 255,
                                      cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image
    img_bin = 255-img_bin  # Invert the image

    # img = np.full((100,80,3), 12, np.uint8)


    # threshold image
    # ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                    # 127, 255, cv2.THRESH_BINARY)
    img = cv2.blur(img,(20,20))

    #cv2.imwrite("Methodology/Image_bin.jpg",img_bin)

    # Defining a kernel length
    kernel_length = np.array(img).shape[1]//400

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect verticle lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
    #cv2.imwrite("Methodology/verticle_lines.jpg",verticle_lines_img)

    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    #cv2.imwrite("Methodology/horizontal_lines.jpg",horizontal_lines_img)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.50
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # For Debugging
    # Enable this line to see verticle and horizontal lines in the image which is used to find boxes
    #cv2.imwrite("Methodology/img_final_bin.jpg",img_final_bin)
    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(
        img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # print(len(contours))
    # Sort all the contours by top to bottom.
    (contours, boundingBoxes) = sort_contours(contours, method="left-to-right")

    x1=-100
    y1=0
    # check=0
    idx = 0
    for c in contours:
        # if check!=3:
            # Returns the location and width,height for every contour
            x, y, w, h = cv2.boundingRect(c)
            # check+=1



            # if ((x==x1)):

            # if(cv2.contourArea(c)>50):
            if(cv2.contourArea(c)>50000):
                # print("no")
                # print(x)
                # print(w)
                # print(h)
                if (w > 300 and h > 400 and((h<(4*w))and(h>(0.6*w))) and(x!=0)):
                    # print("no0")
                    if ((x>(x1+100))): #outer
                    # if ((x<(x1+50))): #inner
                        idx += 1
                        # print("yes")
                        # rect = cv2.minAreaRect(c)
                        # box = cv2.boxPoints(rect)
                        #
                        # box = np.int0(box)
                        # # draw a red 'nghien' rectangle
                        # cv2.drawContours(img, [box], 0, (0, 0, 255))
                        # cv2.imwrite("contour1.png", img)
                        # # finally, get the min enclosing circle


                        # hull = cv.c(points[, hull[, clockwise[, returnPoints]]
                        # hull = cv2.convexHull(c)
                        # print(hull)



                        itr=0

                        approx = cv2.approxPolyDP(c, 0.009 * cv2.arcLength(c, True), True)

    # draws boundary of contours.
                        cv2.drawContours(img3, [approx], 0, (0, 0, 255), 5)

                        # Used to flatted the array containing
                        # the co-ordinates of the vertices.
                        nq = approx.ravel()
                        iq = 0

                        for jq in nq :
                            if(iq % 2 == 0):
                                xq = nq[iq]
                                yq = nq[iq + 1]

                        # String containing the co-ordinates.
                                string = str(xq) + " " + str(yq)

                        #if(i == 0):
                        # text on topmost co-ordinate.
                        # cv2.putText(img2, "Arrow tip", (x, y),
                        # font, 0.5, (255, 0, 0))
                        #else:
                        # text on remaining co-ordinates.
                                cv2.putText(img3, string, (xq, yq),
                                font, 0.5, (255, 255, 0))

                                if(itr==1):
                                    # xq=xq-16
                                    # yq=yq-16
                                    extTop="(%s, %s)" %(xq, yq)
                                if(itr==2):
                                    # xq=xq+16
                                    # yq=yq-16
                                    extRight="(%s, %s)" %(xq, yq)
                                if(itr==3):
                                    # xq=xq+16
                                    # yq=yq+16
                                    extBot="(%s, %s)" %(xq, yq)
                                if(itr==0):
                                    # xq=xq-16
                                    # yq=yq+16
                                    extLeft="(%s, %s)" %(xq, yq)

                                itr = itr + 1

                                # print(xq, yq)
                            iq = iq + 1

                        # Showing the final image.

                        # cv2.imwrite('image2.png', img3)

                        coords="[%s, %s, %s, %s]" %(extTop,extRight,extBot,extLeft)


                        # extLeft = tuple(c[c[:, :, 0].argmin()][0])
                        # extRight = tuple(c[c[:, :, 0].argmax()][0])
                        # extTop = tuple(c[c[:, :, 1].argmin()][0])
                        # extBot = tuple(c[c[:, :, 1].argmax()][0])

                        # hull = []
                        #
                        # # calculate points for each contour
                        #
                        # hull.append(cv2.convexHull(c, False))
                        #
                        # # create an empty black image
                        # drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)
                        #
                        # # draw contours and hull points
                        #
                        # color_contours = (0, 255, 0) # color for contours
                        # color = (255, 255, 255) # color for convex hull
                        # # draw contours
                        # cv2.drawContours(drawing, contours, i, color_contours, 2, 8, hierarchy)
                        # # draw convex hull
                        # cv2.drawContours(drawing, hull, i, color, 2, 8)


                        # extTop="(%s, %s)" %(box[1][0],box[1][1])
                        # extRight="(%s, %s)" %(box[2][0],box[2][1])
                        # extBot="(%s, %s)" %(box[3][0],box[3][1])
                        # extLeft="(%s, %s)" %(box[0][0],box[0][1])

                        # extTop="(%s, %s)" %(box[1][0],box[1][1])
                        # extRight="(%s, %s)" %(box[2][0],box[2][1])
                        # extBot="(%s, %s)" %(box[3][0],box[3][1])
                        # extLeft="(%s, %s)" %(box[0][0],box[0][1])


                        #coords="[%s, %s, %s, %s]" %(extTop,extRight,extBot,extLeft)

                        # print(coords)

                        pts = np.array(eval(coords), dtype = "float32")


                        new_img = four_point_transform(img2,pts)
                        cv2.imwrite(cropped_dir_path+str(idx) + '.png', new_img)
                        # print(x)



                        # box = np.int0(box)
                        # # draw a red 'nghien' rectangle
                        # cv2.drawContours(img, [box], 0, (0, 0, 255))
                        # cv2.imwrite("contour1.png", img)
                        # coords="[(189.96536, 1084.9089), (822.29297, 1050.0603), (990.5377, 2167.3167), (328.2101, 2246.1653)]"
                        # [(189.96536, 1084.9089), (852.29297, 1006.0603), (990.5377, 2167.3167), (328.2101, 2246.1653)]

                    # x1=x #inner

                    # x1=x #inner

                    # y1=y
                        x1=x  #outer
                        # y1=y
                    # print(x)
                    # print(coords)
                    # print(cv2.contourArea(c))

                    # img1 = cv2.imread(img_for_box_extraction_path, 0)  # Read the image
                    # cv2.drawContours(img1,c, -1, (0, 255, 255), 2)
                    # cv2.circle(img1, (189,1084) , 8, (0, 0, 255), -1)
                    # cv2.circle(img1, (852,1006) , 8, (0, 255, 0), -1)
                    # cv2.circle(img1, (990,2167) , 8, (255, 0, 0), -1)
                    # cv2.circle(img1, (328,2246) , 8, (255, 255, 0), -1)
                    # cv2.imwrite('new.png', img1)


                    # if((extLeft[1])>(extBot[1])):
                    #     coords="[%s, %s, %s, %s]" %(extLeft,extTop,extRight,extBot)
                    #
                    # else:
                    #     coords="[%s, %s, %s, %s]" %(extTop,extRight,extBot,extLeft)

                    # print (extLeft)
                    # print ("    ")
                    # print(extRight)
                    # print ("    ")
                    # print (extTop)
                    # print ("    ")
                    # print(extBot)
                    # print ("\n")

                    # box = cv2.boxPoints(c)

                    # coords=(str1+ (extLeft) + str3 + (extTop)+ str3 +(extRight)+ str3 + (extBot)+str2)


                    # print(coords)

                    # print (x1)
                    # print ("    ")
                    # print(w)
                    # print ("\n")
                    # print (h)
                    # print ("\n")




            # If the box height is greater then 20, widht is >80, then only save it as a box in "cropped/" folder.
            # if (w > 40 and h > 60) and (w<1000) and (h > 1.5*w):


    # For Debugging
    # Enable this line to see all contours.
    # cv2.drawContours(img, contours, -1, (0, 0, 255), 3)
    # cv2.imwrite("./Temp/img_contour.jpg", img)

def registration():

    for k in range(1,2):
        if k!=26 and k!=48:
            for p in range(1,4):

                img1_color = cv2.imread("RUN/Cropped/ROLLNO_"+str(k) + "/" +str(p)+ ".png")
                img2_color = cv2.imread("RUN/Cropped/ANSWER_KEY/"+str(p)+".png")

                img1 = cv2.cvtColor(img1_color, cv2.COLOR_BGR2GRAY)
                img2 = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)
                height, width = img2.shape

                p1=box_extractionqw("RUN/Cropped/ROLLNo_"+str(k) + "/" +str(p)+ ".png")
                p2=box_extractionqw("RUN/Cropped/ANSWER_KEY/"+str(p)+".png")

                homography, mask = cv2.findHomography(np.float32(p1), np.float32(p2), cv2.RANSAC)
                transformed_img = cv2.warpPerspective(img1_color, homography, (width, height))
                img2 = cv2.imread("RUN/Cropped/ANSWER_KEY/"+str(p)+".png")
                img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
                img1 = cv2.cvtColor(transformed_img,cv2.COLOR_BGR2GRAY)

                kernel = np.ones((2,2), np.uint8)
                thresh1 = cv2.erode(img1,kernel,iterations=2)
                thresh1 = cv2.dilate(thresh1,kernel,iterations=2)
                ret,thresh1 = cv2.threshold(thresh1,127,255,cv2.THRESH_BINARY_INV)

                thresh2 = cv2.erode(img2,kernel,iterations=2)
                thresh2 = cv2.dilate(thresh2,kernel,iterations=2)
                ret,thresh2 = cv2.threshold(thresh2,127,255,cv2.THRESH_BINARY_INV)

                img3 = cv2.absdiff(thresh1, thresh2)
                kernel3 = np.ones((5,5),np.uint8)
                erosion3 = cv2.erode(img3,kernel3,iterations = 2)
                dilation3 = cv2.dilate(erosion3,kernel3,iterations = 1)
                cropped=dilation3[20:int(.98*len(dilation3)),20:int(.98*(len(dilation3[0])))]
                cv2.imwrite("RUN/Difference/ROLLNO_"+ str(k) +"/Filled/" +str(p)+".png", cropped)
                cv2.imwrite("RUN/Registered/ROLLNO_"+ str(k) +"/Filled/" +str(p)+".png", transformed_img)




                img1_color = cv2.imread("RUN/Cropped/ROLLNO_"+str(k) + "/" +str(p)+ ".png")
                img2_color = cv2.imread("RUN/Cropped/OMR/"+str(p)+".png")

                img1 = cv2.cvtColor(img1_color, cv2.COLOR_BGR2GRAY)
                img2 = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)
                height, width = img2.shape

                p1=box_extractionqw("RUN/Cropped/ROLLNo_"+str(k) + "/" +str(p)+ ".png")
                p2=box_extractionqw("RUN/Cropped/OMR/"+str(p)+".png")

                homography, mask = cv2.findHomography(np.float32(p1), np.float32(p2), cv2.RANSAC)
                transformed_img = cv2.warpPerspective(img1_color, homography, (width, height))
                img2 = cv2.imread("RUN/Cropped/OMR/"+str(p)+".png")
                img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
                img1 = cv2.cvtColor(transformed_img,cv2.COLOR_BGR2GRAY)

                kernel = np.ones((2,2), np.uint8)
                thresh1 = cv2.erode(img1,kernel,iterations=2)
                thresh1 = cv2.dilate(thresh1,kernel,iterations=2)
                ret,thresh1 = cv2.threshold(thresh1,127,255,cv2.THRESH_BINARY_INV)

                thresh2 = cv2.erode(img2,kernel,iterations=2)
                thresh2 = cv2.dilate(thresh2,kernel,iterations=2)
                ret,thresh2 = cv2.threshold(thresh2,127,255,cv2.THRESH_BINARY_INV)

                img3 = cv2.absdiff(thresh1, thresh2)
                kernel3 = np.ones((5,5),np.uint8)
                erosion3 = cv2.erode(img3,kernel3,iterations = 2)
                dilation3 = cv2.dilate(erosion3,kernel3,iterations = 1)
                cropped=dilation3[20:int(.98*len(dilation3)),20:int(.98*(len(dilation3[0])))]
                cv2.imwrite("RUN/Difference/ROLLNO_"+ str(k) +"/Empty/" +str(p)+".png", cropped)
                cv2.imwrite("RUN/Registered/ROLLNO_"+ str(k) +"/Empty/" +str(p)+".png", transformed_img)


def components():

    for j in range(1,2):

        if j!=26 and j!=48:
            cans=0
            cattempted=0
            c1ans=0
            c1attempted=0

            for p in range(1,4):

                inputs = cv2.imread("RUN/Difference/ROLLNO_"+ str(j) +"/Filled/" + str(p) + ".png",0)
                kernel3 = np.ones((5,5),np.uint8)
                erosion3 = cv2.erode(inputs,kernel3,iterations = 3)
                dilation3 = cv2.dilate(erosion3,kernel3,iterations = 3)
                ret, thresh = cv2.threshold(dilation3, 150, 255, cv2.THRESH_BINARY_INV)
                img = cv2.bitwise_not(thresh)
                _, markers = cv2.connectedComponents(img)
                c1ans = np.amax(markers) #total number of connected components with filled anwerkey
                #print(c1ans)
                cans=c1ans+cans



                inputs = cv2.imread("RUN/Difference/ROLLNO_"+ str(j) +"/Empty/" + str(p) + ".png",0)
                kernel3 = np.ones((5,5),np.uint8)
                erosion3 = cv2.erode(inputs,kernel3,iterations = 3)
                dilation3 = cv2.dilate(erosion3,kernel3,iterations = 3)
                ret, thresh = cv2.threshold(dilation3, 150, 255, cv2.THRESH_BINARY_INV)
                img = cv2.bitwise_not(thresh)
                _, markers = cv2.connectedComponents(img)
                c1attempted = np.amax(markers) #total number of connected components with empty OMR
                #print(c1attempted)
                cattempted=c1attempted+cattempted
                # print("kartik")




            cunattempt=30-cattempted  #total number of un attempted question

            # c2unattempt=20-cattempted #total number of un attempted question
            wrongattempt=cans-cunattempt #total number of wrong components
            # wrong2attempt=c2ans-c2unattempt  #total number of wrong components
            # print(count_0)
            wrongattempt=wrongattempt/2
            score=cattempted-wrongattempt
            # print(count_1)
            # score2=c2attempted-wrong2attempt/2
            # print(score1)
            # print(score2)
            # print(The marks of RollNO")
            #print(cans)
            #print(cattempted)
            # print("Score of roll number",j, " is ",score," out of 30")
            return [cattempted,cunattempt,wrongattempt,score];


def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")

	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]

	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect

	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))

	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

	# return the warped image
	return warped

def box_extractionqw(img_for_box_extraction_path):

    img = cv2.imread(img_for_box_extraction_path, 0)  # Read the image
    img2 = cv2.imread(img_for_box_extraction_path, 0)
    img3 = cv2.imread(img_for_box_extraction_path, 0)
    font = cv2.FONT_HERSHEY_COMPLEX
    # img = cv2.blur(img,(10,10))
    (thresh, img_bin) = cv2.threshold(img, 128, 255,
                                      cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image
    img_bin = 255-img_bin  # Invert the image

    # img = np.full((100,80,3), 12, np.uint8)


    # threshold image
    # ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                    # 127, 255, cv2.THRESH_BINARY)
    img = cv2.blur(img,(20,20))

    #cv2.imwrite("Methodology/Image_bin.jpg",img_bin)

    # Defining a kernel length
    kernel_length = np.array(img).shape[1]//400

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect verticle lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
    #cv2.imwrite("Methodology/verticle_lines.jpg",verticle_lines_img)

    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    #cv2.imwrite("Methodology/horizontal_lines.jpg",horizontal_lines_img)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.50
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # For Debugging
    # Enable this line to see verticle and horizontal lines in the image which is used to find boxes
    #cv2.imwrite("Methodology/img_final_bin.jpg",img_final_bin)
    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(
        img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # print(len(contours))
    # Sort all the contours by top to bottom.
    (contours, boundingBoxes) = sort_contours(contours, method="left-to-right")

    x1=0
    y1=0
    # check=0
    idx = 0
    for c in contours:
        # if check!=3:
            # Returns the location and width,height for every contour
            x, y, w, h = cv2.boundingRect(c)
            # check+=1



            # if ((x==x1)):

            if(cv2.contourArea(c)>30000):
            # if ((x>(x1+100))): #outer
                if (w > 300 and h > 400 and((h<(6*w))and(h>(0.3*w)))):
                    if ((x<(x1+100))): #inner
                        idx += 1


                        itr=0

                        approx = cv2.approxPolyDP(c, 0.009 * cv2.arcLength(c, True), True)

    # draws boundary of contours.
                        cv2.drawContours(img3, [approx], 0, (0, 0, 255), 5)
                        #print(len(approx[1]))

                        # Used to flatted the array containing
                        # the co-ordinates of the vertices.
                        nq = approx.ravel()
                        #print(nq)
                        iq = 0

                        for jq in nq :
                            if(iq % 2 == 0):
                                xq = nq[iq]
                                yq = nq[iq + 1]

                        # String containing the co-ordinates.
                                string = str(xq) + " " + str(yq)


                                cv2.putText(img3, string, (xq, yq),
                                font, 0.5, (255, 255, 0))

                                if(itr==1):
                                    # xq=xq-16
                                    # yq=yq-16
                                    extTop=[xq,yq]
                                if(itr==2):
                                    # xq=xq+16
                                    # yq=yq-16
                                    extRight=[xq,yq]
                                if(itr==3):
                                    # xq=xq+16
                                    # yq=yq+16
                                    extBot=[xq,yq]
                                if(itr==0):
                                    # xq=xq-16
                                    # yq=yq+16
                                    extLeft=[xq,yq]

                                itr = itr + 1

                                # print(xq, yq)
                            iq = iq + 1

                        # Showing the final image.

                        # cv2.imwrite('image2.png', img3)

                        coords=[extTop,extRight,extBot,extLeft]
                        # print(coords)
                        #ignore below part and don't erase it
                        sum0=coords[0][0]+coords[0][1]
                        sum1=coords[1][0]+coords[1][1]
                        sum2=coords[2][0]+coords[2][1]
                        sum3=coords[3][0]+coords[3][1]
                        dif0=coords[0][0]-coords[0][1]
                        dif1=coords[1][0]-coords[1][1]
                        dif2=coords[2][0]-coords[2][1]
                        dif3=coords[3][0]-coords[3][1]
                        smin=min(sum0,sum1,sum2,sum3)
                        smax=max(sum0,sum1,sum2,sum3)
                        dmin=min(dif0,dif1,dif2,dif3)
                        dmax=max(dif0,dif1,dif2,dif3)
                        if smin==sum0:
                            tl=[coords[0][0],coords[0][1]]
                        elif smin==sum1:
                            tl=[coords[1][0],coords[1][1]]
                        elif smin==sum2:
                            tl=[coords[2][0],coords[2][1]]
                        elif smin==sum3:
                            tl=[coords[3][0],coords[3][1]]
                        #print(tl)
                        if smax==sum0:
                            br=[coords[0][0],coords[0][1]]
                        elif smax==sum1:
                            br=[coords[1][0],coords[1][1]]
                        elif smax==sum2:
                            br=[coords[2][0],coords[2][1]]
                        elif smax==sum3:
                            br=[coords[3][0],coords[3][1]]
                        #print(br)
                        if dmin==dif0:
                            bl=[coords[0][0],coords[0][1]]
                        elif dmin==dif1:
                            bl=[coords[1][0],coords[1][1]]
                        elif dmin==dif2:
                            bl=[coords[2][0],coords[2][1]]
                        elif dmin==dif3:
                            bl=[coords[3][0],coords[3][1]]
                        #print(bl)
                        if dmax==dif0:
                            tr=[coords[0][0],coords[0][1]]
                        elif dmax==dif1:
                            tr=[coords[1][0],coords[1][1]]
                        elif dmax==dif2:
                            tr=[coords[2][0],coords[2][1]]
                        elif dmax==dif3:
                            tr=[coords[3][0],coords[3][1]]
                        #print(tr)
                        rect=[tl,tr,bl,br]

                        return rect


                        print (coords)

                        x1=x #inner


# p=box_extractionqw("cropped/rollno38/2.png")
# print(p)






if __name__ == '__main__':

	app.run(debug = True)
