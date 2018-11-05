# General Ensemble - find overlapping boxes of the same class and average their 
# positions while adding their confidences. Can weigh different detectors with 
# different weights.
# No real learning here, although the weights and iou_thresh can be optimized.
# 
# Input: 
#  - dets : List of detections. Each detection is all the output from one 
#           detector, and should be a list of boxes, where each box should be 
#           on the format [xim, ymin, xmax, ymax, confidence ]. values 
#           should be floats, except the class which should be an integer.
# 
#  - iou_thresh: Threshold in terms of IOU where two boxes are considered the 
#                same, if they also belong to the same class.
#                
#  - weights: A list of weights, describing how much more some detectors should
#             be trusted compared to others. The list should be as long as the
#             number of detections. If this is set to None, then all detectors
#             will be considered equally reliable. The sum of weights does not
#             necessarily have to be 1.
# 
# Output:
#     A list of boxes, on the same format as the input.
# ==============================================================================
r""" Ensembling methods for object detection. This shows how to merge boxes"""


def GeneralEnsemble(dets, iou_thresh = 0.5, weights=None):
    # number of det model methods 
    ndets = len(dets)
    if weights is None:
        w = 1 / float(ndets)
        weights = [w] * ndets
    else:
        assert(len(weights) == ndets)
        for i in range(len(weights)):
            s = sum(weights)
            weights[i] /= s
        

    out = []
    used = []
    
    for idet in range(0, ndets):
        det = dets[idet]
        for box in det:
            if box in used:
                continue
                
            used.append(box)
            # Search the other detectors for overlapping box of same class
            found = []
            for iodet in range(0, ndets):
                odet = dets[iodet]
                
                if odet == det:
                    continue
                
                bestbox = None
                bestiou = iou_thresh
                for obox in odet:
                    if not obox in used:
                        # Not already used
                        
                        iou = cal_iou(box, obox)
                        if iou > bestiou:
                            bestiou = iou
                            bestbox = obox
                                
                if not bestbox is None:
                    w = weights[iodet]
                    found.append((bestbox,w))
                    used.append(bestbox)
                            
            # Now we've gone through all other detectors
            if len(found) == 0:
                new_box = list(box)
                new_box[-1] /= ndets
                out.append(new_box)
            else:
                allboxes = [(box, weights[idet])]
                allboxes.extend(found)
                
                xc = 0.0
                yc = 0.0
                bw = 0.0
                bh = 0.0
                conf = 0.0
                
                wsum = 0.0
                for bb in allboxes:
                    w = bb[1]
                    wsum += w

                    b = bb[0]
                    xc += w * b[0]
                    yc += w * b[1]
                    bw += w * b[2]
                    bh += w * b[3]
                    conf += w * b[5]
                
                xc /= wsum
                yc /= wsum
                bw /= wsum
                bh /= wsum    

                new_box = [xc, yc, bw, bh, box[4], conf]
                out.append(new_box)
    return out
    
    
def cal_iou(boxA, boxB):
    x11, x12, y11, y12 = boxA[:4]
    x21, x22, y21, y22 = boxB[:4]
    
    x_left   = max(x11, x21)
    y_top    = max(y11, y21)
    x_right  = min(x12, x22)
    y_bottom = min(y12, y22)

    if x_right < x_left or y_bottom < y_top:
        return 0.0    
        
    intersect_area = (x_right - x_left) * (y_bottom - y_top)
    boxA_area = (x12 - x11) * (y12 - y11)
    boxB_area = (x22 - x21) * (y22 - y21)        
    
    iou = intersect_area / (boxA_area + boxB_area - intersect_area)
    return iou
    

if __name__=="__main__":
    # Toy example
    dets = [ 
        [[0.5, 0.5, 1.5, 1.5, 0.9], [0.8, 0.7, 1.5, 2.2, 0.9]], # model1
        [[0.5, 0.3, 1.4, 1.3, 0.8]],                               # model2
        [[4.0, 3.7, 5.2, 4.9, 0.5]]                                # model3
        ]
    
    ens = GeneralEnsemble(dets, weights = [1.0, 0.1, 0.5])
    print(ens)