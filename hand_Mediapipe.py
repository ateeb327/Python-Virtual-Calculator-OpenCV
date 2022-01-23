import cv2
import mediapipe as mp
import math

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class calc_buttons:
  def __init__(self,pos,calc_pt1,calc_pt2, sign):
      self.pos = pos
      self.calc_pt1 = calc_pt1
      self.calc_pt2 = calc_pt2
      self.sign = sign
  def draw(self,img):
    cv2.rectangle(img, self.pos, (self.calc_pt1,self.calc_pt2),(50,50,50), 2)
    cv2.putText(img,self.sign,(self.pos[0]+30,self.pos[1]-25), \
      cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(200,50,0),2)
    
  def draw_circles(x1,y1,x2,y2,imag):
    cv2.circle(imag, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
    cv2.circle(imag, (x2, y2),8,(255,0,255),cv2.FILLED)
    cv2.line(imag, (x1, y1), (x2, y2), (255, 0, 255), 3)

  def find_distance(x1,y1,x2,y2):
    distance = math.hypot(x2-x1,y2-y1) #find hypotenuse of right triangle
    return distance 
  
  def click_check(self,x,y,img):
    if (340<x<420 and 50<y<100):
      return "C"
    if (self.pos[0] < x < self.pos[0] + 80) and ( self.pos[1]-80 < y < self.pos[1]): 
      # cv2.rectangle(img,(100,100), (420,420), (200,200,200), cv2.FILLED)
      # cv2.rectangle(img,(100,100), (420,420), (50,50,50),2) 
      # cv2.rectangle(img, self.pos, (self.calc_pt1,self.calc_pt2),(150,150,150), 2)
      cv2.putText(img,self.sign,(self.pos[0]+20,self.pos[1]-20), \
        cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,2,(200,50,0),2)
      return self.sign
      # for button_pos in button_positions:
      #     # print(element)
      #   if button_pos[0] < x < button_pos[1]:  
      #       cv2.putText(img,self.sign,(self.pos[0]+25,self.pos[1]-20), \
      #         cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,2,(200,50,0),2)
      
    
  



#starting camera
cap = cv2.VideoCapture(0)
cap.set(3,1080) #width #1080
cap.set(4,720) #height #729

calc_signs = [['7','8','9','*'],['4','5','6','-'],['1','2','3','+'],['.','0','=','/']]

buttonList = []
button_positions = []
for x in range(4):
  for y in range(4):
    xpos = x*80 + 100
    ypos = y*80+180
    button_positions.append([xpos,ypos])
    buttonList.append(calc_buttons((xpos,ypos),ypos,xpos,calc_signs[y][x]))
    
#global Variables
#Equation
equation = ""
counter = 0 #to remove duplicates
    
#process with mediapipe library
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    h, w, c = image.shape
    
    #save hand_landmarks in this list
    landmarks = []

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    #print(results)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mylmList = []
        xList = []
        yList = []

        #Hand coordinates x and y
        for id, lm in enumerate(hand_landmarks.landmark):
          px, py = int(lm.x * w), int(lm.y * h)
          mylmList.append([px, py])
          
          xList.append(px)
          yList.append(py)
        landmarks = mylmList
        #box
        xmin, xmax = min(xList), max(xList)
        ymin, ymax = min(yList), max(yList)
        boxW, boxH = xmax - xmin, ymax - ymin
        box = xmin, ymin, boxW, boxH
        cx, cy = box[0] + (box[2] // 2), \
                 box[1] + (box[3] // 2)
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        cv2.rectangle(image, (box[0] - 20, box[1] - 20),
                      (box[0] + box[2] + 20, box[1] + box[3] + 20),
                      (255, 0, 255), 2)
        
    #Designing Main Calculator
    cv2.rectangle(image,(100,100), (420,420), (200,200,200), cv2.FILLED) #Main Box
    cv2.rectangle(image,(100,100), (420,420), (50,50,50),2) #Main Boundary
    
    cv2.rectangle(image,(100,50), (340,100), (200,200,200), cv2.FILLED) #Results pane
    cv2.rectangle(image,(100,50), (420,100), (50,50,50),2)
    #C Button
    cv2.rectangle(image,(340,50), (420,100), (200,200,200), cv2.FILLED) # C Button Box
    cv2.rectangle(image,(340,50), (420,100), (50,50,50), 2) # Boundary
    cv2.putText(image,"C",(365,92), \
      cv2.FONT_HERSHEY_PLAIN,3,(200,50,0),3)

    

    for b in buttonList:
      b.draw(image) 
    
      
    
    #check for hands
    try:
      if hands: #landmark[8] = index finger
        #print(landmarks[8] , landmarks[4])
        x1,y1 = landmarks[8]
        x2,y2 = landmarks[12]
        distance_bw_fingers = calc_buttons.find_distance(x1,y1,x2,y2)
        # button1 = buttonList[0]
        # print(button1.sign)
        # print("Landmarks of index: ",x1,y1)
        # print(distance_bw_fingers)
        #print(buttonList)
        calc_buttons.draw_circles(x1,y1,x2,y2,image)
        
        if distance_bw_fingers < 35:
          for button in buttonList:
            returned_sign = button.click_check(x1,y1,image)
            
            if (returned_sign and counter == 0): #is a string value
              
              if (returned_sign == "="):
                equation = str(eval(equation))
              elif(returned_sign == "C"):
                equation = ""
              else:
                equation = equation + returned_sign
              counter = 1
                
              
            
        
        
      else:
        print('Problem!')
    except:
      pass
      # print("Hand not found!")
    # Flip the image horizontally for a selfie-view display.
    # print(button_positions)
    if (counter !=0):
      counter += 1
      if counter > 10:
        counter = 0
    print(equation)
    cv2.putText(image,equation, (120,85), \
      cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(200,50,0),2)
    cv2.imshow('Hand Tracking', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
