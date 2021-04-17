import cv2
from math import hypot
import simpleaudio
import numpy as np
import time

class Guitar:

  def __init__(self):
    # self.last_strum = time.time()
    self.last_chord = '1_'


  # ---------------------------------------------------------------------------
  # ASSIGN_POINTS
  # scale guitar neck depending on players distance from webcam
  # ---------------------------------------------------------------------------
  def assign_points(self, human):
    self.neck_x = int(human.center_x - (300 * human.hip_width/100))
    self.neck_y = int(human.center_y - (100 * human.hip_width/100))

    self.neck_start = np.array([human.center_x, human.center_y])
    self.neck_end   = np.array([self.neck_x, self.neck_y])


  # ---------------------------------------------------------------------------
  # STRUM_LISTENER
  # handles strumming logic
  # ---------------------------------------------------------------------------
  def strum_listener(self, frame, human):
    # make sure we don't trigger multiple strums from small
    # handmovements
    # if self.last_strum > (time.time() - 0.1):
    #   return

    # get distance right hand has moved in the y direction by
    # comparing current hand position to previous values
    distance = human.rhand_y - human.prev_rhand_y

    # calculate derviative of distance to get our velocity
    velocity = np.sqrt(distance ** 2) / 1

    # define strum area
    tlx = int(human.center_x - human.hip_width/1.5)
    tly = int(human.center_y - human.hip_width/2)
    brx = int(human.center_x + human.hip_width/1.5)
    bry = int(human.center_y + human.hip_width/2)

    strum = ''

    # if right hand is over the strum area
    if (tly < human.rhand_y < bry) and (tlx < human.rhand_x < brx):
      # a positive distance means movement down, negative is up
      # also only register distance of more than 500 to avoid
      # duplicate strums when not moving over the strings
      if distance > 500: # down strum
        if 10 < velocity < 50: # slow strum
          strum = 'down_slow'
        elif velocity > 70: # fast strum
          strum = 'down_fast'
      elif  distance < 500: # up strum
        if 10 < velocity < 50: # slow strum
          strum = 'up_slow'
        elif velocity > 70: # fast strum
          strum = 'up_fast'

    chord = self.fret_listener(frame, human)

    if strum:
      self.play(strum, chord)
      # self.last_strum = time.time()
      self.last_chord = chord


  # ---------------------------------------------------------------------------
  # FRET_LISTENER
  # handles fretboard / chord logic
  # ---------------------------------------------------------------------------
  def fret_listener(self, frame, human):
    # calculate neck length
    neck_len = hypot(self.neck_start[0] - self.neck_end[0], \
                     self.neck_start[1] - self.neck_end[1])
    # initialise chord
    chord = ''

    # step along the neck at intervals, checking if lhand is near
    for p in np.linspace(self.neck_start, self.neck_end, 20):

      hand_distance_from_neck = hypot(human.lhand_x - p[0], \
                                      human.lhand_y - p[1])

      if hand_distance_from_neck < 40: # hand is touching the neck

        # grab the coordinates of the left hand
        x = int(p[0])
        y = int(p[1])

        # calculate how far along the neck the hand is
        distance_from_end = hypot(x - self.neck_x, y - self.neck_y)
        percent = int((distance_from_end / neck_len) * 100)

        # split neck into 3 in order to grab the correct chord sample
        if 0 < percent < 33:
          chord = '1_'
        elif 33 < percent < 66:
          chord = '2_'
        elif 66 < percent < 100:
          chord = '3_'

        cv2.circle(frame, (x,y), 10, (0,255,0), -1)
        break

    return chord

  # ---------------------------------------------------------------------------
  # PLAY
  # loads and plays the correct audio file
  # ---------------------------------------------------------------------------
  def play(self, strum, chord):
    # assemble the filename from chord and strum info
    if chord != '':
      audio_filename = 'audio/' + chord + strum + '.wav'
    else:
      audio_filename = 'audio/' + '1_' + strum + '.wav'

    # stop player if theres a different chord sounding
    # (makes for more natural sound)
    if self.last_chord != chord:
      simpleaudio.stop_all()

    # play the audio file
    simpleaudio.WaveObject.from_wave_file(audio_filename).play()


  # ---------------------------------------------------------------------------
  # DRAW
  # adds either cv drawn graphics or guitar img to the frame
  # ---------------------------------------------------------------------------
  def draw(self, frame, human, draw=0):
    if draw == 0:
      frame = self.draw_guitar(frame, human)
    else:
      frame = self.overlay_guitar(frame, human)
    return frame

  # ---------------------------------------------------------------------------
  # DRAW_GUITAR
  # Draws rudimentary guitar shape using opencv
  # ---------------------------------------------------------------------------
  def draw_guitar(self, frame, human):
    # body
    frame = cv2.ellipse(frame, (human.center_x, human.center_y), \
                       (100,70), 15, 0, 360, (255,0,0), -1)
    # neck
    frame = cv2.line(frame, (human.center_x, human.center_y), \
                     (self.neck_x, self.neck_y),(255,0,0),30)

    return frame

  # ---------------------------------------------------------------------------
  # OVERLAY_TRANSPARENT
  # Overlays an img over the frame, maintaining transparency
  # ---------------------------------------------------------------------------
  def overlay_transparent(self, background, overlay, x, y):
      background_width = background.shape[1]
      background_height = background.shape[0]

      if x >= background_width or y >= background_height:
          return background

      h, w = overlay.shape[0], overlay.shape[1]

      if x + w > background_width:
          w = background_width - x
          overlay = overlay[:, :w]

      if y + h > background_height:
          h = background_height - y
          overlay = overlay[:h]

      if overlay.shape[2] < 4:
          overlay = np.concatenate(
              [
                  overlay,
                  np.ones((overlay.shape[0],
                           overlay.shape[1], 1),
                          dtype = overlay.dtype) * 255
              ],
              axis = 2,
          )
      overlay_image = overlay[..., :3]
      mask = overlay[..., 3:] / 255.0

      background[y:y+h, x:x+w] = (1.0 - mask) * \
                                 background[y:y+h, x:x+w] + \
                                 mask * \
                                 overlay_image
      return background

  # ---------------------------------------------------------------------------
  # OVERLAY_GUITAR
  # Superimposes a scalable guitar image over the webcam frame
  # ---------------------------------------------------------------------------
  def overlay_guitar(self, frame, human):
    guitar_img = cv2.imread('mustang.png', -1)
    # get guitar dimensions for resizing

    guitar_w = int(guitar_img.shape[1] / (135/human.hip_width))
    guitar_h = int(guitar_img.shape[0] / (135/human.hip_width))

    # resize guitar based on distance from camera
    guitar_img = cv2.resize(guitar_img, \
                                 (guitar_w, guitar_h), \
                                 interpolation = cv2.INTER_AREA)

    # find insertion point for guitar image
    guitar_x = human.lhip_x - int(guitar_w/1.5)

    # return if the guitar doesnt fit on the screen
    if guitar_x < 0:
      return frame

    # overlay guitar image over webcam frame
    frame = self.overlay_transparent(frame, guitar_img, guitar_x, \
                                     int(human.center_y-guitar_h/1.5))
    return frame



