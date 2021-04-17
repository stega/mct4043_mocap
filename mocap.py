import cv2
import mediapipe as mp
from human import Human
from guitar import Guitar

# -----------------------------------------------------------------------------
# AIR GUITAR GENERATOR
# -----------------------------------------------------------------------------

# use built in webcam
cap = cv2.VideoCapture(0)

# initalise MediaPipe pose objects
mp_pose    = mp.solutions.pose
pose       = mp_pose.Pose(upper_body_only=True)

# create our Human, passing in the width/height of webcam frame
human = Human(cap.get(3), cap.get(4))
# create our Guitar
guitar = Guitar()

while(True):
  # read in from webcam
  ret, frame = cap.read()

  # flip the frame
  frame = cv2.flip(frame, 1)

  # convert to RGB for processing
  frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  # makes processing more efficient
  frameRGB.flags.writeable = False
  # do the processing!
  results = pose.process(frameRGB)

  if results.pose_landmarks:
    # update our human and guitar with current pose data
    human.assign_hand_and_hip_points(results.pose_landmarks)
    guitar.assign_points(human)

    # draw guitar onto frame
    frame = guitar.draw(frame, human, 1)

    # detect playing of guitar
    guitar.strum_listener(frame, human)

    # save previous hand positions
    human.prev_rhand_x = human.rhand_x
    human.prev_rhand_y = human.rhand_y

  # display
  cv2.imshow('window',frame)

  if cv2.waitKey(20) == ord('q'):
    break

# -----------------------------------------------------------------------------
# clean up
cap.release()
cv2.destroyAllWindows()