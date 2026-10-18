import cv2
from ultralytics import YOLO

""" Loading Pretrained Models:


chessboard_hand.pt - Crops the image to chessboard boundary. Latest Version can crop image accuractely even if hand present over the board/Corner of ChessBoard not visible properly due to hand placement


pieces_hand_fallen.pt - detects pieces/hand/fallen pieces on the cropped board picture


"""






"""

Origin is top left:
+X is measured as we go right
+Y is measured as we go down


"""



board_model = YOLO("Models/chessboard_hand.pt")
pieces_model = YOLO("Models/pieces_hand_fallen.pt")








#This function returns (error if any, cropped board)
def Model_1_ChessboardLocationPrediction_and_Cropping(cv2_imread_frame):

    # Feed the uncropped Image to Model-1
    board_results = board_model(cv2_imread_frame, conf=0.5, verbose=False)
    board_cropped = None
    error_Model1 = False



    #here r gives the result of the particular image we processed, in this case we are feeding it only 1 image of chessboard but in general it allows you to process multiple images and return results in an array
    r = board_results[0]
    #r.boxes is the list of all individual bounding boxes that the model detected inside the image. in our general case only 1 chesboard will be there in the photo and hence only 1 chessboard boundary detected in the photo
    #box represents the single detected object
    if len(r.boxes)>0:
        box = r.boxes[0]
        # bx1, by1, bx2, by2 are the detected chessboard coordinates in the order xmin, ymin, xmax, ymax
        xmin, ymin, xmax, ymax = map(int, box.xyxy[0])

        #cv2.imread object "frame" takes ymin, ymax, xmin and xmax in this order
        extracted_board = cv2_imread_frame[ymin:ymax, xmin:xmax]

        board_cropped = cv2.resize(extracted_board, (800, 800))
    else:
        error_Model1 = True
        board_cropped = "Error: Chessboard not detected in the Image"

    return error_Model1, board_cropped




#This function returns (if hand detected, if fallen pieces, nested array of piece coordinates, squares on chessboard which are occupied)
def Model_2_Pieces_Hand_Fallen_Prediction(board_cropped):

    # Run Model 2 on the cropped board
    pieces_results = pieces_model(board_cropped, conf=0.5, verbose=False)
    # Fetch the class on which I trained Model 2
    class_names = pieces_model.names  # {'fallen_piece', 'hand', 'piece'}



    hand_detected = False
    fallen_piece_detected = False
    piece_boxes = []
    occupied_squares = []




    #Again here pieces_results returns an array for multiple images that you have passed, we have passed only 1 so we just want the first result(Zeroeth index)
    r = pieces_results[0]
    for box in r.boxes:
        #box.cls represents the class_id of the class to which the box belongs. class: ['fallen_piece', 'hand', 'piece'] maps to class_id: [0, 1, 2] 
        cls_id = int(box.cls[0])
        cls_name = class_names[cls_id]  # Matches Label Name ['fallen_piece', 'hand', 'piece'] to class id [0, 1, 2]

        #Again gives xmin, ymin, xmax, ymax of box considered in the looped iteration
        x1, y1, x2, y2 = map(int, box.xyxy[0]) 
            
        # Matc
        if cls_name == "hand":
            hand_detected = True
            break
        elif cls_name == "fallen_piece":
            fallen_piece_detected = True
            break
        elif cls_name == "piece":
            centre_x = (x1+x2)/2
            centre_y = (y1+y2)/2

            height, width = board_cropped.shape[:2]

            unit_block_size = height/8

            floor_x = centre_x//unit_block_size
            floor_y = centre_y//unit_block_size

            piece_boxes.append((x1, y1, x2, y2))
            occupied_squares.append([floor_x, floor_y])


    return hand_detected, fallen_piece_detected, piece_boxes, occupied_squares




#This function displays the image with pieces marked by boxes
def display_PieceBoxed_Image(board_cropped, piece_boxes):
    print("Rendering piece boxes and their centres")

    display_image = board_cropped.copy()

    # No hand or fallen pieces -> Draw upright piece bounding boxes & centers
        
    for (x1, y1, x2, y2) in piece_boxes:
        # Draws bounding box around piece
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
        # Calculate center coordinate of the box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
            
        # Draw center point dot
        cv2.circle(display_image, (cx, cy), 4, (0, 0, 255), -1)
    # Display result
    cv2.imshow("Chess Pipeline Output", display_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




#This function fills the nested emptyBoardState array with X's wherever piece is present, data of where piece is present is passed to it through occupied_squares
def buildBoardState(emptyBoardState, occupied_squares):
    for x in occupied_squares:
        x_coord = int(x[0])
        y_coord = int(x[1])

        emptyBoardState[y_coord][x_coord] = "X"

    return emptyBoardState
    
        



def get_board_state_from_uncropped_img(frame):
    BoardState = None
    msg = None
    flag = None
    error_Model1, board_cropped = Model_1_ChessboardLocationPrediction_and_Cropping(frame)

    emptyBoardState = [
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.']
    ]





    if error_Model1:
        msg = "Error: No chessboard detected"
        flag = "N-CB"

    else: 
        hand_detected, fallen_piece_detected, piece_boxes, occupied_squares = Model_2_Pieces_Hand_Fallen_Prediction(board_cropped)

        if hand_detected:
            msg = "Hand detected over board. Remove hand to continue."
            flag = "Hand"
        elif fallen_piece_detected:
            msg = "Fallen pieces detected. Reset the pieces to continue."
            flag = "Fallen"
        else:
            msg = "No hand or fallen pieces detected."
            flag = "Valid"
            BoardState = buildBoardState(emptyBoardState, occupied_squares)
            # display_PieceBoxed_Image(board_cropped, piece_boxes)
    return BoardState, msg, flag