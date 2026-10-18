# type: ignore



'''

Four Possibilties:

1) hand in image
2) fallen piece in image
3) rest state, image to X. representation done and its opponents chance
4) rest state, image to X. representation done and its our chance

'''



prevState = ...



while not board.is_game_over():

    uncropped_image = clickImage()
    hand, fallen_pieces, thisState = image_detection_models(uncropped_image)

    if hand or fallen_pieces:
        time.sleep(2)
        continue
    else:
        if (prevState == thisState) and (opponentsChance):
            #Waiting for opponent to move
            time.sleep(2)
            continue
        elif (prevState == thisState) and (ourChance):
            #Waiting for our Player to physically move
            time.sleep(2)
            continue
        elif (prevState != thisState) and (opponentsChance):
            #Just Played out our move, Waiting for player to make a move
            prevState = thisState
            time.sleep(2)
            continue
        elif (prevState != thisState) and (ourChance):
            prevState = thisState
            best_move = getBestmove(thisState)
            print(bestmove)
        